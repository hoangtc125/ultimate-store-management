# -*- coding: utf-8 -*-
"""

An elastic search framework that support ORM-like repository.
The framework provide most basic common CRUD api

How to use:

        # Get object repo
        >>> from app.repo.es_connection import get_repo
        >>> user_repo = get_repo(User)
        >>> user_repo.get_all()
        ...

"""

import math
from typing import (
    List,
    Optional,
    TypeVar,
    Dict)
import asyncio
from uuid import uuid4
import json
from app.utils.els_utils import *

from elasticsearch import (
    AsyncElasticsearch,
    ElasticsearchException,
    NotFoundError)

from app.utils.model_utils import (
    get_dict,
    get_els_response_model
)
from app.core.project_config import settings
from app.core.model import PaginationModel
from app.core.model import ElasticsearchFilter
from app.core.cache import cache_delete

T = TypeVar("T")
es_monitor = {}


class ESRepo:
    """

    The class is a repository which have one connection to els host.
    The connection is used for crud api.
        - get_one: return a tuple (id, model)
        - get-page: return a Pagination model contain: num_data, max_page, current page and data of current page
        - insert: return an inserted id
        - bulk insert: return a list corresponding to the input list: adding success returns id, adding failure returns error
        - update: return updated record id
        - delete: return els response

    Args:
        model (generic type): the representation model for index.
        els_url (str): Elasticsearch URL.

    Attributes:
        es_connector (AsyncElasticsearch): els host connection with APIs,
        model (generic type): .
        idx_name (str):  name of the index in els (model name lowercase).

    """
    def __init__(self, model: T, els_url):
        self.es_connector = AsyncElasticsearch(hosts=[els_url], headers={})
        self.els_url = els_url
        self.model = model
        self.idx_name = model.__name__.lower()
        asyncio.ensure_future(self.create_if_not_exist())

    async def close_connection(self):
        await self.es_connector.close()

    async def create_if_not_exist(self):
        if not (await self.es_connector.indices.exists(index=self.idx_name)):
            await self.es_connector.indices.create(index=self.idx_name)

    async def get_one_by_id(self, doc_id):
        try:
            resp = await self.es_connector.get(index=self.idx_name, id=doc_id)
        except NotFoundError:
            return None
        return (resp["_id"], self.model(**resp["_source"]))

    async def get_all(self, filter: Optional[dict] = None) -> Dict[str, T]:
        body = {
            "query": {"bool": {"must": []}},
        }
        if filter:
            body["query"]["bool"]["must"].append(filter)
        resp = await self.es_connector.search(
            index=self.idx_name, body=body, size=10000
        )
        res = {}
        for item in resp["hits"]["hits"]:
            res[item["_id"]] = get_els_response_model(item, self.model)
        return res

    async def get_all_by_filter(self, filters: List[ElasticsearchFilter]) -> Dict[str, T]:
        body = ElasticsearchFilter.to_els_filter(filters)
        resp = await self.es_connector.search(
            index=self.idx_name, body=body, size=10000
        )
        res = {}
        for item in resp["hits"]["hits"]:
            res[item["_id"]] = get_els_response_model(item, self.model)
        return res

    async def get_page(self, page, size, filters: List[ElasticsearchFilter]):
        if size < 1 or size > 10000:
            raise ElasticsearchException("Size is less than 10001 and greater than 0")
        body = ElasticsearchFilter.to_els_filter(filters)
        body["size"] = size
        resp = await self.es_connector.search(index=self.idx_name, body=body, scroll='1m')
        for i in range(page - 1):
            scroll_id = resp['_scroll_id']
            resp = await self.es_connector.scroll( 
                scroll_id = scroll_id,
                scroll = '1m'
            )
        results = {}
        for hit in resp['hits']['hits']:
            results[hit["_id"]] = get_els_response_model(hit, self.model)
        num_data = resp['hits']['total']['value']
        max_page = int(math.ceil(num_data / size))
        res = PaginationModel(
            num_data = num_data,
            max_page = max_page,
            current_page=page,
            data=results
        )
        return res

    @cache_delete()
    async def insert_one(self, obj: T, custom_id=None):

        if obj.__class__ != self.model:
            raise TypeError(
                f"{obj.__name__} can not be inserted into {self.model.__name__}"
            )
        doc_id = custom_id if custom_id else uuid4()
        els_resp = await self.es_connector.create(
            index=self.idx_name, id=doc_id, body=get_dict(obj)
        )

        return els_resp["_id"]

    async def bulk_manipulate(self, lst_obj: List[T], custom_id: List[str]=None):
        if not custom_id:
            custom_id = [None]*len(lst_obj)
        if len(lst_obj) != len(custom_id):
            raise ElasticsearchException("Length of list id is not equal length of list object")
        data = []
        for i in lst_obj:
            if i.__class__ == self.model:
                continue
            raise TypeError(
                f"Can not be inserted into {self.model.__name__}"
            )

        for obj, id in zip(lst_obj, custom_id):
            _id = id if id != None else str(uuid4())
            row_index = {"index": {"_index": self.idx_name, "_id": _id}}
            row_data = get_dict(obj)
            data.append(row_index)
            data.append(row_data)
        payload = '\n'.join([json.dumps(line) for line in data]) + '\n'
        els_resp = await self.es_connector.bulk(payload)
        res = []
        for els_res in els_resp["items"]:
            res_ = els_res["index"]
            status = els_res["index"]["status"]
            cur_res = res_["_id"] if status != 400 else {"error": res_["error"]}
            res.append(cur_res)
        return res

    async def delete(self, _id):
        resp = await self.es_connector.delete(index=self.idx_name, id=_id)
        return resp

    @cache_delete()
    async def update(self, doc_id, obj):
        if obj.__class__ != self.model:
            raise TypeError(
                f"{obj.__name__} can not be inserted into {self.model.__name__}"
            )
        body = get_dict(obj, allow_none=True)
        resp = await self.es_connector.update(
            index=self.idx_name, id=doc_id, body={"doc": body, "detect_noop": False}
        )
        return resp["_id"]
    
    async def get_one_by_fields(self, fields: list, sort : Optional[list] = None, get_first = False):
        body = {
            "query": {"bool": {"must": []}},
        }
        for field in fields:
            if len(field) != 2:
                raise Exception("Each Field must have exactly 2 values")
            key, value = field
            if key.split(".")[0] not in vars(self.model)["__fields__"]:
                raise Exception(f"Field {key} doesn't appear in fields list")
            body["query"]["bool"]["must"].append({"match": {key: value}})
        if sort:
            body["sort"] = sort

        resp = await self.es_connector.search(index=self.idx_name, body=body)
        if resp["hits"]["total"]["value"] > 1 and not get_first:
            raise ElasticsearchException(
                f"There are more than 1 record with {key} is {value}"
            )
        if resp["hits"]["total"]["value"] == 0:
            return None
        _res = resp["hits"]["hits"][0]
        res = (_res["_id"], self.model(**_res["_source"]))
        return res


def get_repo(model: T, els_url=settings.ELASTIC_URL, new_connection = False) -> ESRepo:
    if new_connection:
        return ESRepo(model, els_url)
    if not es_monitor.get(model.__name__, None):
        es_monitor[model.__name__] = ESRepo(model, els_url)
    return es_monitor[model.__name__]

