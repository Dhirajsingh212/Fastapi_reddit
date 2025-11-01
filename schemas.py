from datetime import datetime

from pydantic import BaseModel
from typing import Optional


class UserRequest(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    status: str = "success"
    message: str = "Successfully done"
    id: int
    username: str
    email: str
    createdAt: datetime
    updatedAt: datetime

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str
