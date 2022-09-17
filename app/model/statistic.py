from typing import Dict, List, Optional
from pydantic import BaseModel

class Statistic(BaseModel):
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


class StatisticCreate(Statistic, BaseModel):
  pass


class StatisticResponse(Statistic, BaseModel):
  id: str