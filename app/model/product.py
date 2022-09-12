from typing import List, Optional
from pydantic import BaseModel

from app.core.model import BaseAuditModel
from app.utils.time_utils import *


class BaseProduct(BaseModel):
    name: Optional[str] = None
    nickname: Optional[List] = None
    priceIn: Optional[int] = None
    brand: Optional[str] = None
    quantity: Optional[int] = None
    priceOut: Optional[int] = None
    images: Optional[List] = []
    created_at: Optional[int] = get_current_timestamp()


class Product(BaseProduct, BaseAuditModel):
    _id: str
    is_disabled: Optional[bool] = False


class ProductCreate(BaseProduct, BaseModel):
    id: str

class ProductUpdate(BaseProduct):
    pass


class ProductResponse(Product):
    id: str


class ProductMinResponse(BaseModel):
    is_disabled: Optional[bool] = False
    id: str
    name: Optional[str] = None
    nickname: Optional[List] = None
    priceIn: Optional[int] = None
    brand: Optional[str] = None
    quantity: Optional[int] = None
    priceOut: Optional[int] = None
    created_at: Optional[int] = get_current_timestamp()

