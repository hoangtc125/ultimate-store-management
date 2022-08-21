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


class CameraAPI(BaseAPIModel):
    TAKE_A_SHOT = '/camera/shot'
    STREAMING = '/camera/streaming'
    SELECT_DEVICE =  '/camera/select'
    PREDICT = '/camera/predict'


ALLOW_ALL = ["*"]

API_PERMISSION = {
    AccountAPI.LOGIN: ALLOW_ALL,
    AccountAPI.REGISTER: [Role.ADMIN],
    AccountAPI.ABOUT_ME: Role.get_all(),
    AccountAPI.GET_ALL: Role.get_all(),
    AccountAPI.DISABLE: Role.get_all(),
    AccountAPI.ENABLE: Role.get_all(),
    AccountAPI.UPDATE: Role.get_all(),
    AccountAPI.UPDATE_PASSWORD: Role.get_all(),
    AccountAPI.UPDATE_STAFF: Role.get_all(),
    AccountAPI.UPDATE_PASSWORD_STAFF: Role.get_all(),
    CameraAPI.TAKE_A_SHOT: ALLOW_ALL,
    CameraAPI.STREAMING: ALLOW_ALL,
    CameraAPI.SELECT_DEVICE: ALLOW_ALL,
    CameraAPI.PREDICT: ALLOW_ALL,
}

WHITE_LIST_IP = {
    "127.0.0.1": [
    ],  
}

WHITE_LIST_PATH = [
    AccountAPI.LOGIN,
]
