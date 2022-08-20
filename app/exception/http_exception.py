from fastapi import HTTPException, status
from app.core.model import response_code


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        error_type,
        message=None,
        headers={"WWW-Authenticate": "Bearer"},
        status_code=status.HTTP_400_BAD_REQUEST
    ):  
        self.error_code = response_code["error"][error_type]["code"]
        self.error_message = message if message else response_code["error"][error_type]["message"]
        self.headers = headers
        self.status_code = status_code
