from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
import subprocess   
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

if __name__ == "__main__":
    command = r'firefox http://localhost:{}'.format(str(settings.FRONTEND_PORT))
    subprocess.Popen(str(command).split(), shell=False)
    uvicorn.run(app2, host="0.0.0.0", port=int(settings.FRONTEND_PORT))
