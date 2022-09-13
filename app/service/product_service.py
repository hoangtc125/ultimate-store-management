from app.core.constants import Role
from app.core.model import ElasticsearchFilter, TokenPayload
from app.core.project_config import settings
from app.core.cache import cache
from app.repo.es_connector import get_repo
from app.exception.http_exception import CustomHTTPException
from app.model.product import *
from app.utils.model_utils import get_dict, to_response_dto
from app.utils.time_utils import *
from app.core.log_config import logger

class ProductService:

    def __init__(self):
        self.product_repo = get_repo(Product)

    async def get_product_by_id(self, product_id: str):
        res = await self.product_repo.get_one_by_id(product_id)
        if res:
            doc_id, product = res
            return to_response_dto(doc_id, product, ProductResponse)
        else:
            return None

    async def create_one_product(self, product_create: ProductCreate, actor=None):
        _product = await self.get_product_by_id(product_create.id)
        if _product:
            raise CustomHTTPException(error_type="product_existed")
        product = Product(
            **get_dict(product_create),
            is_disabled=False,
        )
        product_id = await self.product_repo.insert_one(obj=product, custom_id=product_create.id)
        return to_response_dto(product_id, product, ProductResponse)

    async def update_product(self, product_id: str,  product_update: ProductUpdate, actor: str, role: str):
        res = await self.get_product_by_id(product_id)
        if not res:
            raise CustomHTTPException(error_type="product_not_existed")
        old_product = res
        _product = Product(
            **get_dict(product_update),
            is_disabled=old_product.is_disabled
        )
        doc_id = await self.product_repo.update(doc_id=product_id, obj=_product)
        return to_response_dto(doc_id, _product, ProductResponse)

    async def get_all_active_product(self):
        filter = ElasticsearchFilter(field='is_disabled', match=False)
        products = await self.product_repo.get_all_by_filter(filters=[filter])
        res = []
        for doc_id, product in products.items():
            res.append(to_response_dto(doc_id, product, ProductResponse))
        return res

    async def get_all_min_product(self):
        filter = ElasticsearchFilter(field='is_disabled', match=False)
        products = await self.product_repo.get_all_by_filter(filters=[filter])
        res = []
        for doc_id, product in products.items():
            res.append(to_response_dto(doc_id, product, ProductMinResponse))
        return res

    async def get_all(self):
        products = await self.product_repo.get_all()
        res = []
        for doc_id, product in products.items():
            res.append(to_response_dto(doc_id, product, ProductResponse))
        return res

    async def disable_product(self, product_id: str):
        res = await self.product_repo.get_one_by_id(doc_id=product_id)
        if not res:
            raise CustomHTTPException(error_type="product_not_existed")
        _id, product = res
        if product.is_disabled:
            return product
        product.is_disabled = True
        _product = Product(**get_dict(product))
        doc_id = await self.product_repo.update(doc_id=_id, obj=_product)
        return to_response_dto(doc_id, _product, ProductResponse)

    async def undisabled_product(self, product_id: str):
        res = await self.product_repo.get_one_by_id(doc_id=product_id)
        if not res:
            raise CustomHTTPException(error_type="product_not_existed")
        _id, product = res
        if not product.is_disabled:
            return product
        product.is_disabled = False
        _product = Product(**get_dict(product))
        doc_id = await self.product_repo.update(doc_id=_id, obj=_product)
        return to_response_dto(doc_id, _product, ProductResponse)