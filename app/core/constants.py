from typing import Optional


class Role:
    ADMIN = "ADMIN"
    STAFF = "STAFF"

    @staticmethod
    def get_all():
        return [Role.ADMIN, Role.STAFF]

class DateTime:
    DATE_FORMAT: str = '%Y-%m-%d'
    DATETIME_FORMAT: str = '%Y-%m-%d %H:%M:%S'
    TIME_FORMAT: str = '%H:%M:%S'

class SortOrder:
    DESC = "desc"
    ASC = "asc"

    @staticmethod
    def get_list_sort_order():
        return [SortOrder.DESC, SortOrder.ASC]
