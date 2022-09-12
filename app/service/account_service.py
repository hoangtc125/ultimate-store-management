from typing import Union

from app.core.constants import Role
from app.core.model import ElasticsearchFilter, TokenPayload
from app.core.project_config import settings
from app.core.cache import cache
from app.repo.es_connector import get_repo
from app.exception.http_exception import CustomHTTPException
from app.model.account import *
from app.model.token import *
from app.utils.jwt_utils import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_hashed_password,
    verify_password,
)
from app.utils.model_utils import get_dict, to_response_dto
from app.utils.time_utils import *
from app.core.log_config import logger

class AccountService:

    ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

    def __init__(self):
        self.account_repo = get_repo(Account)
        self.token_repo = get_repo(Token)

    @staticmethod
    def validate_account(account: Union[Account, AccountCreate, AccountUpdate]):
        if account.role not in Role.get_all():
            raise Exception(f"Quyền {account.role} không được hỗ trợ")

    # @cache(reloaded_by=[Account])
    async def get_account_by_username(self, username):
        fields = [("username", username)]
        res = await self.account_repo.get_one_by_fields(fields)
        if not res:
            return None
        id, account = res
        return to_response_dto(id, account, AccountResponse)

    async def get_token_by_username(self, username):
        res = await self.token_repo.get_one_by_id(username)
        if not res:
            return None
        id, token = res
        return to_response_dto(id, token, Token)

    async def get_account_by_id(self, account_id: str):
        res = await self.account_repo.get_one_by_id(account_id)
        if res:
            doc_id, account = res
            return to_response_dto(doc_id, account, AccountResponse)
        else:
            return None

    async def create_one_account(self, account_create: AccountCreate, actor=None):
        _account = await self.get_account_by_username(username=account_create.username)
        if _account:
            raise CustomHTTPException(error_type="account_existed")
        hashed_password = get_hashed_password(account_create.password)
        account = Account(
            hashed_password=hashed_password, **get_dict(account_create, allow_none=True)
        )
        # if account.role == Role.ADMIN:
        #     CustomHTTPException(error_type="create_admin_account")
        try:
            self.validate_account(account)
        except Exception as e:
            raise CustomHTTPException(
                error_type="role_unsupported",
                message=str(e)
            )
        account_id = await self.account_repo.insert_one(obj=account)
        return to_response_dto(account_id, account, AccountResponse)

    async def update_account(self, account_id: str,  account_update: AccountUpdate, actor: str, role: str):
        res = await self.account_repo.get_one_by_id(doc_id=account_id)
        if not res:
            raise CustomHTTPException(error_type="account_not_existed")
        _, old_account = res
        logger.log(account_update.username, old_account.username)
        if account_update.username != old_account.username:
            raise CustomHTTPException(error_type="change_username")
        try:
            self.validate_account(account_update)
        except Exception as e:
            raise CustomHTTPException(
                error_type="role_unsupported",
                message=str(e)
            )
        if actor == old_account.username and old_account.role != account_update.role:
            raise CustomHTTPException(error_type="update_role")
        elif actor != old_account.username:  # admin updates user's profile
            if role != Role.ADMIN:
                raise CustomHTTPException(error_type="permission_denied")
            if old_account.role == Role.ADMIN:
                raise CustomHTTPException(error_type="update_admin_account")
            if account_update.role != old_account.role:  # update user token with new role
                expire_time = get_timestamp_after(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                confirmation_token = create_access_token(
                    id=account_id,
                    data=TokenPayload(username=old_account.username, role=account_update.role, expire_time=expire_time)
                )
                token = await self.get_token_by_username(old_account.username)
                if token:
                    await self.token_repo.update(doc_id=old_account.username, obj=confirmation_token)
        _account = Account(
            **get_dict(account_update),
            hashed_password=old_account.hashed_password,
            is_disabled=old_account.is_disabled
        )
        doc_id = await self.account_repo.update(doc_id=account_id, obj=_account)
        return to_response_dto(doc_id, _account, AccountResponse)

    async def authenticate_user(self, username: str, password: str):
        account = await self.get_account_by_username(username)
        if not account:
            raise CustomHTTPException(error_type="unauthorized")
        if account.is_disabled:
            raise CustomHTTPException(error_type="unauthorized")
        if not verify_password(password, account.hashed_password):
            raise CustomHTTPException(error_type="unauthorized")
        expire_time = get_timestamp_after(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        confirmation_token = create_access_token(
            id=account.id,
            data=TokenPayload(username=username, role= account.role, expire_time=expire_time)
        )
        token = await self.get_token_by_username(username)
        if not token:
            await self.token_repo.insert_one(obj=confirmation_token, custom_id=username)
        elif token.expires_at > get_current_timestamp():
            return (token, account)
        else:
            await self.token_repo.update(doc_id=username, obj=confirmation_token)
        return (confirmation_token, account)

    async def get_all_active_account(self):
        filter = ElasticsearchFilter(field='is_disabled', match=False)
        accounts = await self.account_repo.get_all_by_filter(filters=[filter])
        res = []
        for doc_id, account in accounts.items():
            res.append(to_response_dto(doc_id, account, AccountResponse))
        return res

    async def get_all(self):
        accounts = await self.account_repo.get_all()
        res = []
        for doc_id, account in accounts.items():
            res.append(to_response_dto(doc_id, account, AccountResponse))
        return res

    async def disable_account(self, account_id: str):
        res = await self.account_repo.get_one_by_id(doc_id=account_id)
        if not res:
            raise CustomHTTPException(error_type="account_not_existed")
        _id, account = res
        if account.role == Role.ADMIN:
            raise CustomHTTPException(error_type="update_admin_account")
        if account.is_disabled:
            return account
        account.is_disabled = True
        _account = Account(**get_dict(account))
        doc_id = await self.account_repo.update(doc_id=_id, obj=_account)
        return to_response_dto(doc_id, _account, AccountResponse)

    async def undisabled_account(self, account_id: str):
        res = await self.account_repo.get_one_by_id(doc_id=account_id)
        if not res:
            raise CustomHTTPException(error_type="account_not_existed")
        _id, account = res
        if account.role == Role.ADMIN:
            raise CustomHTTPException(error_type="update_admin_account")
        if not account.is_disabled:
            return account
        account.is_disabled = False
        _account = Account(**get_dict(account))
        doc_id = await self.account_repo.update(doc_id=_id, obj=_account)
        return to_response_dto(doc_id, _account, AccountResponse)
        
    async def update_user_password(self, account_id: str, form_data: PasswordUpdate, role: str):
        if role != Role.ADMIN:
            raise CustomHTTPException(error_type="permission_denied")
        res = await self.account_repo.get_one_by_id(account_id)
        if not res:
            raise CustomHTTPException(error_type="account_not_existed")
        _, account_update = res
        if account_update.role == Role.ADMIN:
            raise CustomHTTPException(error_type="update_admin_account")
        account_update.hashed_password = get_hashed_password(form_data.new_password)
        _account = Account(**get_dict(account_update))
        await self.account_repo.update(doc_id=account_id, obj=_account)
        return "Update password successful!!!"

    async def update_my_password(self, form_data: PasswordUpdate, actor: str):
        account_update = await self.get_account_by_username(actor)
        if not account_update:
            raise CustomHTTPException(error_type="account_not_existed")
        if not form_data.old_password:
            raise CustomHTTPException(error_type="missing_old_password")
        if not verify_password(form_data.old_password, account_update.hashed_password):
            raise CustomHTTPException(error_type="unauthorized")
        account_update.hashed_password = get_hashed_password(form_data.new_password)
        _account = Account(**get_dict(account_update))
        await self.account_repo.update(doc_id=account_update.id, obj=_account)
        return "Update password successful!!!"