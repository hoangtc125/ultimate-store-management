from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.model import HttpResponse, success_response
from app.core.oauth2 import CustomOAuth2PasswordBearer
from app.core.api_config import AccountAPI
from app.core.log_config import logger
from app.service.account_service import AccountService
from app.model.account import *
from app.utils.router_utils import get_actor_from_request, get_role_from_request

router = APIRouter()
oauth2_scheme = CustomOAuth2PasswordBearer(tokenUrl=AccountAPI.LOGIN)

@router.post(AccountAPI.LOGIN)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.log(form_data)
    result = await AccountService().authenticate_user(
        form_data.username, form_data.password
    )
    return {"token_type": result.token_type, "access_token": result.token}

@router.post(AccountAPI.REGISTER, response_model=HttpResponse)
async def register(account_create: AccountCreate, actor=Depends(get_actor_from_request)):
    logger.log(actor, account_create)
    result = await AccountService().create_one_account(account_create)
    return success_response(data=result)

@router.get(AccountAPI.ABOUT_ME)
async def about_me(token: str = Depends(oauth2_scheme), actor=Depends(get_actor_from_request)):
    logger.log(actor, token)
    result = await AccountService().get_account_by_username(actor)
    return success_response(data=result)

@router.get(AccountAPI.GET_ALL)
async def get_all_active_account(
    token: str = Depends(oauth2_scheme),
):
    result = await AccountService().get_all_active_account()
    return success_response(data=result)
