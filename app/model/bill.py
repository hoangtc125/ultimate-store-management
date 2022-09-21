from typing import Dict, List, Optional
from pydantic import BaseModel

class Bill(BaseModel):
  created_at: Optional[str] = None
  totalPrice: Optional[int] = None
  textPrice: Optional[List] = []
  products: Optional[Dict] = {}
  customer: Optional[Dict] = {}
  store: Optional[Dict] = {}
  seller: Optional[Dict] = {}
  status: Optional[str] = ''
  note: Optional[str] = ''
  images: Optional[List] = []


class BillCreate(Bill, BaseModel):
  pass


class BillResponse(Bill, BaseModel):
  id: str

class BillRelationItem(BaseModel):
  id: str
  status: str
  created_at: str

class BillRelation(BaseModel):
  childs: List = []

class BillRelationResponse(BillRelation):
  id: str