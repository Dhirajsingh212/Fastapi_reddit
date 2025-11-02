from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id:int
    username:str
    email:str

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

class PostRequest(BaseModel):
    title: str
    description: str

class PostResponse(BaseModel):
    id: int
    title: str
    description: str
    owner: User
    created_at: datetime
    updated_at: datetime
    message:str = "Successfully done"
    status: str = "success"

class PostUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
