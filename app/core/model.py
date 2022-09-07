from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, TypeVar, List
import json

from app.core.project_config import settings


f_json = open(settings.RESPONSE_CODE_DIR, encoding="utf8")
response_code = json.load(f_json)
T = TypeVar("T")


class BaseAuditModel(BaseModel):

    created_by: str = "system"
    created_at: int = int(datetime.now().timestamp())
    last_modified_by: str = ""
    last_modified_at: int = None


class HttpResponse(BaseModel):

    status_code = response_code["success"]["code"]
    msg = response_code["success"]["message"]
    data: Optional[T] = None

class PaginationModel(BaseModel):
    num_data: int
    max_page: int
    current_page: int
    data: Any

class TokenPayload(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    expire_time: Optional[int] = None

class ElasticsearchFilter(BaseModel):
    field: str
    match: Optional[Any] = None
    unmatch: Optional[Any] = None
    gte: Optional[Any] = None
    lte: Optional[Any] = None
    sort: Optional[Any] = None

    @staticmethod
    def to_els_filter(filters: List):
        body = {
            "query": {"bool": {"must": [], "must_not": []}},
            "sort": []
        }
        for filter in filters:
            if hasattr(filter, 'match') and filter.match != None:
                body["query"]["bool"]["must"].append({"match": {filter.field: filter.match}})
            if hasattr(filter, 'unmatch') and filter.unmatch != None:
                body["query"]["bool"]["must_not"].append({"match": {filter.field: filter.unmatch}})
            if getattr(filter, 'gte'):
                body["query"]["bool"]["must"].append({"range": {filter.field: {"gte": filter.gte}}})
            if getattr(filter, 'lte'):
                body["query"]["bool"]["must"].append({"range": {filter.field: {"lte": filter.lte}}})
            if getattr(filter, 'sort'):
                body["sort"].append({filter.field: {"order": filter.sort}})
        return body


def custom_response(status_code, message: str, data: T) -> HttpResponse:
    return HttpResponse(status_code=status_code, msg=message, data=data)


def success_response(data=None):
    return HttpResponse(status_code=200, msg="Success", data=data)


if __name__ == "__main__":
    a= ElasticsearchFilter("abc")
    print(
        a(match = "123123")
    )
