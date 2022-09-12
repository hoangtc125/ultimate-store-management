from fastapi import APIRouter, Depends

from app.core.model import HttpResponse, success_response
from app.core.api_config import ProductAPI
from app.core.log_config import logger
from app.service.product_service import ProductService
from app.model.product import *
from app.utils.router_utils import get_actor_from_request, get_role_from_request
from app.router.account_router import oauth2_scheme

router = APIRouter()

@router.post(ProductAPI.CREATE, response_model=HttpResponse)
async def create_product(product_create: ProductCreate, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, product_create)
    result = await ProductService().create_one_product(product_create)
    return success_response(data=result)

@router.get(ProductAPI.GET)
async def get(product_id: str, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await ProductService().get_product_by_id(product_id)
    return success_response(data=result)

@router.get(ProductAPI.GET_ALL_ACTIVATE)
async def get_all_active_product():
    result = await ProductService().get_all_active_product()
    return success_response(data=result)

@router.get(ProductAPI.GET_ALL_MIN)
async def get_all_min_product():
    result = await ProductService().get_all_min_product()
    return success_response(data=result)

@router.get(ProductAPI.GET_ALL)
async def get_all():
    result = await ProductService().get_all()
    return success_response(data=result)

@router.put(ProductAPI.UPDATE, response_model=HttpResponse)
async def update(product_id: str, product_update: ProductUpdate, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request), role=Depends(get_role_from_request)):
    logger.log(actor, product_update)
    result = await ProductService().update_product(product_id=product_id, product_update=product_update, actor=actor, role=role)
    return success_response(data=result)

@router.delete(ProductAPI.DISABLE, response_model=HttpResponse)
async def disable(product_id: str, token: str = Depends(oauth2_scheme), role=Depends(get_role_from_request)):
    logger.log(role, product_id)
    result = await ProductService().disable_product(product_id=product_id)
    return success_response(data=result)

@router.put(ProductAPI.UNDISABLED, response_model=HttpResponse)
async def undisabled(product_id: str, token: str = Depends(oauth2_scheme), role=Depends(get_role_from_request)):
    logger.log(role, product_id)
    result = await ProductService().undisabled_product(product_id=product_id)
    return success_response(data=result)
