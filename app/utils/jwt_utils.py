from app.exception.http_exception import CustomHTTPException
from app.model.token import Token
from jose import JWTError, jwt
from app.core import settings
from app.core.model import TokenPayload
from app.utils.time_utils import (
    get_current_timestamp,
    get_timestamp_after
)
from app.utils.model_utils import get_dict
from passlib.hash import bcrypt

# from backend.app.config.config import SecurityConfig
# from backend.app.utils.TimeUtil import TimeUtil


pwd_context = bcrypt
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.SECURITY_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_hashed_password(password):
    return pwd_context.hash(password)


def create_access_token(id: str, data: TokenPayload) -> Token:
    to_encode = get_dict(data)
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return Token(
        account_id=id, token=token, created_at=get_current_timestamp(), expires_at=data.expire_time
    )


def get_token_payload(token: str):
    try:
        payload_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_payload = TokenPayload(**payload_data)
        username: str = token_payload.username
        expire = token_payload.expire_time
        if username is None:
            raise CustomHTTPException(error_type="unauthorized")
        if expire < get_current_timestamp():
            raise CustomHTTPException(error_type="expired_token")
    except JWTError:
        raise CustomHTTPException(error_type="unauthorized")
    return token_payload


if __name__ == "__main__":
    a = get_hashed_password("admin")
