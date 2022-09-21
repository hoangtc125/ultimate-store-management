from typing import List, Optional
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
    ip: str

class DeviceResponse(Device):
    id: str
