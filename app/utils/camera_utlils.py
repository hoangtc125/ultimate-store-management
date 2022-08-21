import requests
import cv2
import numpy as np
import imutils

from app.exception.http_exception import CustomHTTPException

def shot(url):
    try:
        while True:
            img_resp = requests.get(url)
            img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
            img = cv2.imdecode(img_arr, -1)
            img = imutils.resize(img, width=1000, height=1800)
            cv2.imshow("Ultimate Store Management - Streaming", img)
            if cv2.waitKey(1) == 27:
                break
        cv2.destroyAllWindows()
    except:
        raise CustomHTTPException(error_type="ip_camera_error")