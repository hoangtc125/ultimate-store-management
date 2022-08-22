from typing import Dict, Optional
from pydantic import BaseModel, root_validator

from app.core.constants import Role
from app.core.model import BaseAuditModel
from app.exception.http_exception import CustomHTTPException
from app.utils.time_utils import *


class BaseAccount(BaseModel):
    username: str
    fullname: str
    role: str = Role.STAFF
    phone: str
    email: Optional[str] = None
    ratio_salary: float = 1.0
    created_at: int = get_current_timestamp()
    avatar: Optional[str] = None
    birthday: Optional[str] = None
    profile: Optional[Dict] = {}


class Account(BaseAccount, BaseAuditModel):
    _id: str
    hashed_password: str
    is_disabled: Optional[bool] = False


class AccountCreate(BaseAccount, BaseModel):
    password: str


class AccountUpdate(BaseAccount):
    pass


class AccountResponse(Account):
    id: str


class PasswordUpdate(BaseModel):
    old_password: Optional[str] = None
    new_password: str
    repeat_password: str

    @root_validator
    def check_passwords_match(cls, values):
        pw1, pw2 = values.get('new_password'), values.get('repeat_password')
        if pw1 != pw2:
            raise CustomHTTPException(error_type="passwords_miss_matching")
        return values

