from app.repo.es_connector import get_repo
from app.model.store import *
from app.utils.model_utils import get_dict, to_response_dto

class StoreService:

    def __init__(self):
        self.store_repo = get_repo(Store)

    async def get_store_by_id(self):
        res = await self.store_repo.get_one_by_id('store')
        if res:
            doc_id, store = res
            return to_response_dto(doc_id, store, StoreResponse)
        else:
            return None

    async def create_one_store(self, store_create: Store, actor=None):
        store = Store(
            **get_dict(store_create),
        )
        _store = await self.get_store_by_id()
        if _store:
            store_id = await self.store_repo.update(doc_id='store', obj=store)
        else :
            store_id = await self.store_repo.insert_one(obj=store, custom_id='store')
        return to_response_dto(store_id, store, StoreResponse)