import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
import requests
import cv2
import numpy as np
import imutils
import base64
import subprocess
import qrcode
import base64
from tensorflow.keras import models
from io import BytesIO
from PIL import Image
from typing import Any

from app.core.project_config import settings
from app.core.api_config import CameraAPI
from app.core.helpper import mac_from_ip
from app.exception.http_exception import CustomHTTPException
from app.model.camera import *
from app.repo.es_connector import get_repo
from app.utils.camera_utlils import *
from app.utils.img_utils import *
from app.utils.model_utils import get_dict, to_response_dto
from app.service.account_service import AccountService

class CameraService:

    def __init__(self):
        self.camera_repo = get_repo(Camera)

    def take_a_shot(self, ip: str):
        try:
            url = str("http://" + ip + ":8080/photo.jpg")
            img_resp = requests.get(url)
            img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
            img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            img = cv2.cvtColor(img , cv2.COLOR_BGR2RGB)
            img = imutils.resize(img, width=settings.IMAGE_WIDTH, height=settings.IMAGE_HEIGHT)
            img = Image.fromarray(img)
            img.show()
            im_file = BytesIO()
            img.save(im_file, format="JPEG")
            im_bytes = im_file.getvalue()  # im_bytes: image in binary format.
            im_b64 = base64.b64encode(im_bytes)
            return im_b64
        except:
            raise CustomHTTPException(error_type="ip_camera_error")

    def generate_qrcode(self, actor=""):
        hostname = subprocess.run(str("hostname -I").split(), stdout=subprocess.PIPE).stdout.decode('utf-8').split(" ")[0]
        ping_request = str(hostname + ':' + settings.BACKEND_PORT + CameraAPI.REGISTER + '?account=' + actor)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=4,
            border=4,
        )
        qr.add_data(ping_request)
        qr.make(fit=True)
        img = qr.make_image()
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str 

    async def register(self, ip: str, actor):
        mac = mac_from_ip(ip)
        if not mac:
            raise CustomHTTPException(error_type="ip_camera_error")
        res = await self.camera_repo.get_one_by_id(mac)
        if not res:
            camera = Camera(owner=actor, mac_wifi=mac, ip=ip)
            camera_id = await self.camera_repo.insert_one(obj=camera, custom_id=mac)
            return to_response_dto(camera_id, camera, CameraResponse)
        else:
            id, camera = res
            camera.owner = actor
            camera_id = await self.camera_repo.update(doc_id=id, obj=camera)
            return to_response_dto(camera_id, camera, CameraResponse)

    async def select_device(self):
        cameras = await self.camera_repo.get_all()
        res = []
        for doc_id, camera in cameras.items():
            account = await AccountService().get_account_by_username(camera.owner)
            if not account:
                continue
            device = Device(owner=camera.owner, fullname=account.fullname, ip=camera.ip)
            res.append(get_dict(device))
        return res

    def predictBase64(self, listString, path):
        answer = []
        classes=[]
        imgPredict = []
        for _,dirs,_ in os.walk(path + r'/data'):
            classes=dirs
            break
        classes = sorted(classes)
        print(classes)
        for i in listString:
            binaryImg = i.encode('ascii')
            with open("imagePredict.png", "wb") as fh:
                fh.write(base64.decodebytes(binaryImg))
            imgPre = cv2.imread("imagePredict.png")
            imgPre = cv2.cvtColor(imgPre, cv2.COLOR_BGR2RGB)
            print(imgPre.shape)
            imgPredict.append(imgPre)
        model = models.load_model(path + r'/model')
        imgPredict = np.array(imgPredict)
        encodePre = np.argmax(model.predict(imgPredict), axis=-1)
        print(encodePre)
        for i in encodePre:
            answer.append(classes[i]) 
        return answer

