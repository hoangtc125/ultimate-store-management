from app.repo.es_connector import get_repo
from app.model.bill import *
from app.utils.model_utils import get_dict, to_response_dto

class BillService:

    def __init__(self):
        self.bill_repo = get_repo(Bill)

    async def get_bill_by_id(self, bill_id: str):
        res = await self.bill_repo.get_one_by_id(bill_id)
        if res:
            doc_id, bill = res
            return to_response_dto(doc_id, bill, BillResponse)
        else:
            return None

    async def create_one_bill(self, bill_create: BillCreate, actor=None):
        bill = Bill(
          **get_dict(bill_create),
        )
        bill_id = await self.bill_repo.insert_one(obj=bill)
        return to_response_dto(bill_id, bill, BillResponse)

    async def get_all(self):
        bills = await self.bill_repo.get_all()
        res = []
        for doc_id, bill in bills.items():
            res.append(to_response_dto(doc_id, bill, BillResponse))
        return res