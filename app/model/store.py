from typing import Optional
from pydantic import BaseModel


class Store(BaseModel):
  name: Optional[str] = ""
  owner: Optional[str] = ""
  phone: Optional[str] = ""
  address: Optional[str] = ""


class StoreResponse(Store):
  id: str