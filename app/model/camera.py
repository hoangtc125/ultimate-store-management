from typing import Optional
from pydantic import BaseModel


class BaseCamera(BaseModel):
    mac: str
    ip: str

class Camera(BaseCamera):
    pass

class CameraResponse(BaseCamera):
    id: str