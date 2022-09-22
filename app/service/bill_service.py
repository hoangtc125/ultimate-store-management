from app.exception.http_exception import CustomHTTPException
from app.repo.es_connector import get_repo
from app.model.bill import *
from app.service.product_service import ProductService
from app.utils.model_utils import get_dict, to_response_dto

class BillService:

    def __init__(self):
        self.bill_repo = get_repo(Bill)
        self.bill_relation_repo = get_repo(BillRelation)

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
        for id, quantity in bill.products.items():
            if (bill.status == 'refund'):
                await ProductService().bulk_update(id, -int(quantity))
            elif (bill.status == 'pay1'):
                pass
            else:
                await ProductService().bulk_update(id, int(quantity))
        if bill.status in ['pay', 'debt']:
            await self.create_relation(bill_id)
        return to_response_dto(bill_id, bill, BillResponse)

    async def get_all(self):
        bills = await self.bill_repo.get_all()
        res = []
        for doc_id, bill in bills.items():
            res.append(to_response_dto(doc_id, bill, BillResponse))
        return res

    async def create_relation(self, id):
        billRelation = BillRelation(childs=[])
        bill_relation_id = await self.bill_relation_repo.insert_one(obj=billRelation, custom_id=id)
        return bill_relation_id

    async def get_relation(self):
        bills = await self.bill_relation_repo.get_all()
        res = []
        for doc_id, bill in bills.items():
            res.append(to_response_dto(doc_id, bill, BillRelationResponse))
        return res

    async def into_relation(self, id, billRelationItem):
        res = await self.bill_relation_repo.get_one_by_id(id)
        if not res:
            raise CustomHTTPException(error_type="relation_not_existed")
        relation_id, relation = res
        relation.childs.append(get_dict(billRelationItem))
        doc_id = await self.bill_relation_repo.update(doc_id=relation_id, obj=relation)
        return doc_id
