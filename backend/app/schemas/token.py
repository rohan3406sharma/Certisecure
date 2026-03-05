from __future__ import annotations
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    type: str
    role: str = "user"


class RefreshRequest(BaseModel):
    refresh_token: str
