from typing import Any
from fastapi import APIRouter, Depends

from app.core.model import HttpResponse, success_response
from app.core.api_config import CameraAPI
from app.core.log_config import logger
from app.service.camera_service import CameraService
from app.model.account import *
from app.utils.router_utils import get_actor_from_request, get_role_from_request


router = APIRouter()

@router.get(CameraAPI.SELECT_DEVICE, response_model=HttpResponse)
async def select_device(actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = CameraService().select_device()
    return success_response(data=result)

@router.post(CameraAPI.TAKE_A_SHOT, response_model=HttpResponse)
async def take_a_shot(device: str, actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = CameraService().take_a_shot(device=device)
    return success_response(data=result)

@router.post(CameraAPI.STREAMING, response_model=HttpResponse)
async def streaming(device: str, actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = CameraService().streaming(device=device)
    return success_response(data=result)

@router.post(CameraAPI.PREDICT, response_model=HttpResponse)
async def predict(img: Any, actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, role)
    result = await CameraService().predict(img=img)
    return success_response(data=result)