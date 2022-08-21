import threading
from typing import Any
import requests
import cv2
import numpy as np
import imutils
import base64
from PIL import Image
import subprocess

from app.core.project_config import settings
from app.exception.http_exception import CustomHTTPException
from app.utils.camera_utlils import *

class CameraService:

    def __init__(self):
        pass

    def take_a_shot(self, device: str):
        try:
            ip = device.split(" ")[1][1:-1]
            url = str("http://" + ip + ":8080/photo.jpg")
            img_resp = requests.get(url)
            img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
            img = cv2.imdecode(img_arr, -1)
            img = imutils.resize(img, width=settings.IMAGE_WIDTH, height=settings.IMAGE_HEIGHT)
            Image.fromarray(img, 'RGB').show()
            return base64.b64encode(img_arr)
        except:
            raise CustomHTTPException(error_type="ip_camera_error")

    def streaming(self, device: str):
        try:
            ip = device.split(" ")[1][1:-1]
            url = str("http://" + ip + ":8080/photo.jpg")
            threading.Thread(target=shot, args=(url, ), daemon=True).start()
            return None
        except:
            raise CustomHTTPException(error_type="ip_camera_error")

    def select_device(self):
        devices = subprocess.run(str("arp -a").split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
        res = [device for device in devices.split("\n") if device]
        return res

    async def predict(self, img: Any):
        pass

if __name__ == "__main__":
    CameraService().take_a_shot(device="OPPO-F11-Pro (192.168.1.222) at 82:23:09:0f:d2:46 [ether] on wlo1")
