from fastapi import Request

def get_actor_from_request(request: Request):
    return request._headers['x-request-user']

def get_role_from_request(request: Request):
    return request._headers['x-request-role']