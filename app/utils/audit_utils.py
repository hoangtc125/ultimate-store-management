from typing import TypeVar
from app.utils.time_utils import get_current_timestamp

T = TypeVar("T")

def add_audit_create(actor, target: T) -> T:
    if not hasattr(target, 'created_by') and not hasattr(target, 'created_at'):
        raise Exception(
            message=f"Object do not have created_by or create_at attribute"
        )
    else:
        target.created_by = actor
        target.created_at = get_current_timestamp()
        return target

def add_audit_update(actor, target: T) -> T:
    if not hasattr(target, 'last_modified_by') and not hasattr(target, 'last_modified_at'):
        raise Exception(
            message=f"Object do not have last_modified_by or last_modified_at attribute"
        )
    target.last_modified_by = actor
    target.last_modified_at = get_current_timestamp()
    return target
