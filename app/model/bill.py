from typing import Dict, List, Optional
from pydantic import BaseModel

from app.utils.time_utils import get_current_timestamp

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


class BillCreate(Bill, BaseModel):
  pass


class BillResponse(Bill, BaseModel):
  id: str