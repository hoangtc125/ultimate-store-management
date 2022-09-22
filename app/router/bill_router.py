from fastapi import APIRouter, Depends

from app.core.model import HttpResponse, success_response
from app.core.api_config import BillAPI
from app.core.log_config import logger
from app.service.bill_service import BillService
from app.model.bill import BillCreate, BillRelationItem
from app.utils.router_utils import get_actor_from_request
from app.router.account_router import oauth2_scheme

router = APIRouter()

@router.post(BillAPI.CREATE, response_model=HttpResponse)
async def create_bill(bill_create: BillCreate, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, bill_create)
    result = await BillService().create_one_bill(bill_create)
    return success_response(data=result)

@router.get(BillAPI.GET)
async def get(bill_id: str, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await BillService().get_bill_by_id(bill_id)
    return success_response(data=result)

@router.get(BillAPI.GET_ALL)
async def get_all(token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await BillService().get_all()
    return success_response(data=result)

@router.get(BillAPI.GET_RELATION)
async def get_relation(token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await BillService().get_relation()
    return success_response(data=result)

@router.post(BillAPI.INTO_RELATION)
async def into_relation(id: str, billRelationItem: BillRelationItem, token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await BillService().into_relation(billRelationItem=billRelationItem, id=id)
    return success_response(data=result)