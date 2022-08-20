from pydantic import BaseModel


class Token(BaseModel):
    token_type: str = "Bearer"
    token: str
    created_at: int
    expires_at: int
