import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
# from app.core.socket import socket_connection
from app.core.filter import authorize_token, check_api_permission
from app.exception.http_exception import CustomHTTPException
from app.core.api_config import WHITE_LIST_PATH
from app.core.log_config import logger
from app.core import settings

from app.router import (
    account_router,
    camera_router,
    product_router,
    store_router,
    bill_router,
)


app = FastAPI(version=1.0, debug=False, title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_middleware(request: Request, call_next):
    start_time = time.time()
    request_user = None
    if request.method != "OPTIONS" and (request.url.path not in WHITE_LIST_PATH):
        try:
            request_user = authorize_token(
                request=request
            )
        except CustomHTTPException as e:
            json_res = JSONResponse(
                status_code=e.status_code,
                headers={'access-control-allow-origin': '*', "X-Process-Time":str(time.time() - start_time)},
                content=jsonable_encoder({
                    "status_code": e.error_code,
                    "msg": e.error_message
                }),
            )
            return json_res
    logger.log(request, request_user, tag=logger.tag.START)
    if request.method != "OPTIONS" and (request.url.path not in WHITE_LIST_PATH):
        try:
            check_api_permission(
                path=request.url.path,
                request_role=request_user.role,
                request_host=request.client.host,
            )
        except CustomHTTPException as e:
            json_res = JSONResponse(
                status_code=e.status_code,
                headers={'access-control-allow-origin': '*', "X-Process-Time":str(time.time() - start_time)},
                content=jsonable_encoder({
                    "status_code": e.error_code,
                    "msg": e.error_message
                }),
            )
            logger.log(request.url.path, json_res, tag=logger.tag.END)
            return json_res
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.log(request.url.path, response, tag=logger.tag.END)
    return response

@app.exception_handler(CustomHTTPException)
async def uvicorn_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.error_code,
            "msg": exc.error_message
        }
    )

app.include_router(account_router.router)
app.include_router(camera_router.router)
app.include_router(product_router.router)
app.include_router(store_router.router)
app.include_router(bill_router.router)

if __name__ == "__main__":
    """
        How to run:
        >>> conda create --name usm python=3.6.13
        >>> conda activate usm
        >>> pip install -r requirements
        >>> export PYTHONPATH=$PWD
        >>> python app/application.py
    """
    uvicorn.run(app, host="0.0.0.0", port=int(settings.BACKEND_PORT))
