from app.core import settings
from app.core.constants import Role


class BaseAPIModel:
    @property
    def ALL(self):
        lst_api = [v for v in self.__class__.__dict__.values() if v not in ['__main__', None]]
        return lst_api


class AccountAPI(BaseAPIModel):
    LOGIN = '/account/login'
    REGISTER = "/account/register"
    ABOUT_ME = "/account/me"
    GET_ALL = "/account/get-all"
    DISABLE = "/account/disable"
    ENABLE = "/account/enable"
    UPDATE = "/account/update"
    UPDATE_PASSWORD = "/account/update-password"
    UPDATE_STAFF = "/account/update-staff"
    UPDATE_PASSWORD_STAFF = "/account/update-password-staff"


ALLOW_ALL = Role.get_all()

API_PERMISSION = {
    AccountAPI.LOGIN: ALLOW_ALL,
    AccountAPI.REGISTER: ALLOW_ALL,
    AccountAPI.ABOUT_ME: ALLOW_ALL,
    AccountAPI.GET_ALL: [Role.ADMIN],
    AccountAPI.DISABLE: ALLOW_ALL,
    AccountAPI.ENABLE: ALLOW_ALL,
    AccountAPI.UPDATE: ALLOW_ALL,
    AccountAPI.UPDATE_PASSWORD: ALLOW_ALL,
    AccountAPI.UPDATE_STAFF: ALLOW_ALL,
    AccountAPI.UPDATE_PASSWORD_STAFF: ALLOW_ALL,
}

WHITE_LIST_IP = {
    "127.0.0.1": [
    ],  
}

WHITE_LIST_PATH = [
    AccountAPI.LOGIN,
]
