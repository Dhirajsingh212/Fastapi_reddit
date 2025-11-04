from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class User(BaseModel):
    id:int
    username:str
    email:str

class UserRequest(BaseModel):
    username: str = Field(min_length=5)
    email: str = EmailStr()
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

class PostResponseWithComments(PostResponse):
    total_comments: int

class PostUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class CommentRequest(BaseModel):
    comment:str = Field(min_length=5)

class CommentResponse(BaseModel):
    id: int
    comment:str
    owner: User
    post: PostResponse
    created_at: datetime
    updated_at: datetime
    message:str = "Successfully done"
    status: str = "success"

class CommentWithUserDetails(BaseModel):
    id: int
    comment:str
    owner: User
    message:str = "Successfully done"
    status: str = "success"

class CommentUpdateRequest(BaseModel):
    comment: Optional[str] = Field(None, min_length=5)