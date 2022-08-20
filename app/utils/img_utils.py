# import base64
# import numpy as np
# import cv2


# def resize_avatar(input):
#     imgdata = base64.b64decode(input.split("base64,")[-1])
#     nparr = np.frombuffer(imgdata, np.uint8)
#     img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     h, w, _ = img_np.shape
#     if h > w:
#         if h > 200:
#             new_h = 200
#             new_w = int(200 / h * w)
#         else:
#             new_h = h
#             new_w = w
#     else:
#         if w > 200:
#             new_w = 200
#             new_h = int(200 / w * h)
#         else:
#             new_h = h
#             new_w = w
#     img_np = cv2.resize(img_np, (new_w, new_h))
#     retval, buffer = cv2.imencode(".jpg", img_np)
#     img = base64.b64encode(buffer).decode("utf-8")
#     return img
