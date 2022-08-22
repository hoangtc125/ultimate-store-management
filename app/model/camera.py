from typing import Optional
from pydantic import BaseModel


class BaseCamera(BaseModel):
    owner: str
    mac_wifi: str
    ip: str

class Camera(BaseCamera):
    pass

class CameraResponse(BaseCamera):
    id: str

class Device(BaseModel):
    owner: str
    fullname: str
    role: str
    phone: str
    avatar: Optional[str] = None
    ip: str

class DeviceResponse(Device):
    id: str