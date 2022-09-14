from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
# from winreg import HKEY_CLASSES_ROOT, HKEY_CURRENT_USER, OpenKey, QueryValueEx
# import subprocess   
# import platform
# import shutil
import uvicorn


from app.core.project_config import settings

app2 = FastAPI(version=1.0)

@app2.middleware("http")
async def add_request_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.endswith('.js'):
        response.headers["content-type"] = "application/javascript"
    elif request.url.path.endswith('.html'):
        response.headers["content-type"] = "text/html"
    elif request.url.path.endswith('.ico'):
        response.headers["content-type"] = "image/x-icon"
    return response

@app2.get("/health-check")
def health_check():
    return "Run"

@app2.get("/")
async def get_ui():
    with open(settings.UI_DIR + r'/index.html', encoding="utf8") as fh:
        data = fh.read()
    return Response(content=data, media_type="text/html")

app2.mount("/static", StaticFiles(directory= settings.UI_DIR + r'/static'), name="ui")

@app2.exception_handler(404)
async def custom_404_handler(_, __):
    with open(settings.UI_DIR + r'/index.html', encoding="utf8") as fh:
        data = fh.read()
    return Response(content=data, media_type="text/html")

# def get_default_browser_path():
#     browser_path = shutil.which('open')
#     osPlatform = platform.system()
#     if osPlatform == 'Windows':
#         try:
#             with OpenKey(HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice') as regkey:
#                 browser_choice = QueryValueEx(regkey, 'ProgId')[0]
#             with OpenKey(HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(browser_choice)) as regkey:
#                 browser_path_tuple = QueryValueEx(regkey, None)
#                 browser_path = browser_path_tuple[0].split('"')[1]
#             return browser_path
#         except Exception:
#             return "chrome.exe"
#     else:
#         return "chrome.exe"

if __name__ == "__main__":
    # command = r'cmd.exe /c start "" "{}" -app=http://localhost:{}'.format(get_default_browser_path(), str(settings.FRONTEND_PORT))
    # subprocess.Popen(str(command), shell=False)
    uvicorn.run(app2, host="0.0.0.0", port=int(settings.FRONTEND_PORT))
