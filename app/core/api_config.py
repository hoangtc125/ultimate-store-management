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
    GET_ALL_ACTIVE = "/account/get-all-active"
    DISABLE = "/account/disable"
    UNDISABLED = "/account/undisabled"
    ENABLE = "/account/enable"
    UPDATE = "/account/update"
    UPDATE_PASSWORD = "/account/update-password"
    UPDATE_STAFF = "/account/update-staff"
    UPDATE_PASSWORD_STAFF = "/account/update-password-staff"


class CameraAPI(BaseAPIModel):
    CONTROL = '/camera/controll'
    TAKE_A_SHOT = '/camera/shot'
    QR_CODE = '/camera/qr'
    SELECT_DEVICE =  '/camera/select'
    PREDICT = '/camera/predict'
    REGISTER = '/camera/register'


ALLOW_ALL = ["*"]

API_PERMISSION = {
    AccountAPI.LOGIN: ALLOW_ALL,
    AccountAPI.REGISTER: ALLOW_ALL,
    AccountAPI.ABOUT_ME: Role.get_all(),
    AccountAPI.GET_ALL_ACTIVE: Role.get_all(),
    AccountAPI.GET_ALL: [Role.ADMIN],
    AccountAPI.DISABLE: [Role.ADMIN],
    AccountAPI.UNDISABLED: [Role.ADMIN],
    AccountAPI.ENABLE: Role.get_all(),
    AccountAPI.UPDATE: Role.get_all(),
    AccountAPI.UPDATE_PASSWORD: Role.get_all(),
    AccountAPI.UPDATE_STAFF: [Role.ADMIN],
    AccountAPI.UPDATE_PASSWORD_STAFF: [Role.ADMIN],
    CameraAPI.CONTROL: Role.get_all(),
    CameraAPI.TAKE_A_SHOT: Role.get_all(),
    CameraAPI.QR_CODE: Role.get_all(),
    CameraAPI.SELECT_DEVICE: Role.get_all(),
    CameraAPI.PREDICT: Role.get_all(),
    CameraAPI.REGISTER: ALLOW_ALL,
}

WHITE_LIST_IP = {
    "127.0.0.1": [
    ],  
}

WHITE_LIST_PATH = [
    AccountAPI.LOGIN,
    '/socket.io/',
]
