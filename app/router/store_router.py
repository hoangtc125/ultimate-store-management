from fastapi import APIRouter, Depends

from app.core.model import HttpResponse, success_response
from app.core.api_config import StoreAPI
from app.core.log_config import logger
from app.service.store_service import StoreService
from app.model.store import *
from app.utils.router_utils import get_actor_from_request
from app.router.account_router import oauth2_scheme

router = APIRouter()

@router.post(StoreAPI.UPDATE, response_model=HttpResponse)
async def create_store(store_create: Store, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, store_create)
    result = await StoreService().create_one_store(store_create)
    return success_response(data=result)

@router.get(StoreAPI.GET)
async def get(token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await StoreService().get_store_by_id()
    return success_response(data=result)
