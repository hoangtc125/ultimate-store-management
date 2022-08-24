from typing import Any
from fastapi import APIRouter, Depends, Request

from app.core.model import HttpResponse, success_response
from app.core.api_config import CameraAPI
from app.core.log_config import logger
from app.service.camera_service import CameraService
from app.model.account import *
from app.utils.router_utils import get_actor_from_request, get_role_from_request
from app.router.account_router import oauth2_scheme


router = APIRouter()

@router.get(CameraAPI.QR_CODE, response_model=HttpResponse)
async def qr_code(token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = CameraService().generate_qrcode(actor)
    return success_response(data=result)

@router.get(CameraAPI.REGISTER, response_model=HttpResponse)
async def register(account: str, request: Request, actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = await CameraService().register(request.__dict__["scope"]["client"][0], account)
    return success_response(data=result)

@router.get(CameraAPI.SELECT_DEVICE, response_model=HttpResponse)
async def select_device(token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = await CameraService().select_device()
    return success_response(data=result)

@router.post(CameraAPI.TAKE_A_SHOT, response_model=HttpResponse)
async def take_a_shot(ip: str, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = CameraService().take_a_shot(ip=ip)
    return success_response(data=result)

@router.post(CameraAPI.PREDICT, response_model=HttpResponse)
async def predict(img: Any, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = await CameraService().predict(img=img)
    return success_response(data=result)