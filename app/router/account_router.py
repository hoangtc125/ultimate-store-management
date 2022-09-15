from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.model import HttpResponse, success_response
from app.core.oauth2 import CustomOAuth2PasswordBearer
from app.core.api_config import AccountAPI
from app.core.log_config import logger
from app.service.account_service import AccountService
from app.model.account import *
from app.service.store_service import StoreService
from app.utils.router_utils import get_actor_from_request, get_role_from_request

router = APIRouter()
oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl=AccountAPI.LOGIN)

@router.post(AccountAPI.LOGIN)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.log(form_data)
    result, account = await AccountService().authenticate_user(
        form_data.username, form_data.password
    )
    store = await StoreService().get_store_by_id()
    return {"token_type": result.token_type, "access_token": result.token, "account": account, "store": store}

@router.post(AccountAPI.REGISTER, response_model=HttpResponse)
async def register(account_create: AccountCreate, actor=Depends(get_actor_from_request)):
    logger.log(actor, account_create)
    result = await AccountService().create_one_account(account_create)
    return success_response(data=result)

@router.get(AccountAPI.ABOUT_ME)
async def about_me(token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await AccountService().get_account_by_username(actor)
    return success_response(data=result)

@router.get(AccountAPI.GET_ALL_ACTIVE)
async def get_all_active_account(
    token: str = Depends(oauth2_scheme),
):
    result = await AccountService().get_all_active_account()
    return success_response(data=result)

@router.get(AccountAPI.GET_ALL)
async def get_all(
    token: str = Depends(oauth2_scheme),
):
    result = await AccountService().get_all()
    return success_response(data=result)

@router.put(AccountAPI.UPDATE, response_model=HttpResponse)
async def update(account_id: str, account_update: AccountUpdate, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, account_update)
    result = await AccountService().update_account(account_id=account_id, account_update=account_update, actor=actor, role=role)
    return success_response(data=result)

@router.put(AccountAPI.UPDATE_PASSWORD, response_model=HttpResponse)
async def update_password(password_update: PasswordUpdate, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, password_update)
    result = await AccountService().update_my_password(form_data=password_update, actor=actor)
    return success_response(data=result)

@router.put(AccountAPI.UPDATE_STAFF, response_model=HttpResponse)
async def update_staff(account_id: str, account_update: AccountUpdate, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, account_update)
    result = await AccountService().update_account(account_id=account_id, account_update=account_update, actor=actor, role=role)
    return success_response(data=result)

@router.put(AccountAPI.UPDATE_PASSWORD_STAFF, response_model=HttpResponse)
async def update_password_staff(account_id: str, password_update: PasswordUpdate, token: str = Depends(oauth2_scheme), role=Depends(get_role_from_request)):
    logger.log(role, password_update)
    result = await AccountService().update_user_password(account_id=account_id, form_data=password_update, role=role)
    return success_response(data=result)

@router.delete(AccountAPI.DISABLE, response_model=HttpResponse)
async def disable(account_id: str, token: str = Depends(oauth2_scheme), role=Depends(get_role_from_request)):
    logger.log(role, account_id)
    result = await AccountService().disable_account(account_id=account_id)
    return success_response(data=result)

@router.put(AccountAPI.UNDISABLED, response_model=HttpResponse)
async def undisabled(account_id: str, token: str = Depends(oauth2_scheme), role=Depends(get_role_from_request)):
    logger.log(role, account_id)
    result = await AccountService().undisabled_account(account_id=account_id)
    return success_response(data=result)
