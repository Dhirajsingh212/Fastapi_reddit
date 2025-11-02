from typing import List

from fastapi import APIRouter, HTTPException,Path
from sqlalchemy.orm import lazyload, joinedload
from starlette import status
import schemas
from schemas import PostRequest, PostResponse, PostUpdateRequest
from dependency import user_dependency,db_dependency
from database.models import User, Post

router = APIRouter(
    prefix="/posts",
    tags=["posts"],
)

@router.post("/",response_model=PostResponse,status_code=status.HTTP_201_CREATED)
async def create_new_post(user:user_dependency,db:db_dependency,post_request:PostRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized"
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    post_model = Post(
        title=post_request.title,
        description=post_request.description,
        owner_id=user_model.id,
        owner=user_model
    )
    db.add(post_model)
    db.commit()
    db.refresh(post_model)

    return PostResponse(
        id=post_model.id,
        title=post_model.title,
        description=post_model.description,
        owner=schemas.User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email
        ),
        message="Post created",
        created_at=post_model.created_at,
        updated_at=post_model.updated_at,
    )

@router.get("/user/all",response_model=List[PostResponse],status_code=status.HTTP_200_OK)
async def get_user_all_posts(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized"
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    post_models = (db
                   .query(Post)
                   .filter(Post.owner_id == user_model.id)
                   .options(joinedload(Post.owner))
                   .all()
                   )

    return post_models

@router.get("/all",response_model=List[PostResponse],status_code=status.HTTP_200_OK)
async def get_all_post(db:db_dependency):
    post_model = db.query(Post).options(joinedload(Post.owner)).all()
    return post_model

@router.put("/{post_id}",response_model=PostResponse,status_code=status.HTTP_200_OK)
async def update_user_post(user:user_dependency,db:db_dependency,post_request:PostUpdateRequest,post_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized"
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    post_model = db.query(Post).filter(Post.id == post_id).first()
    if post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post_model.owner_id != user_model.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of the post"
        )

    updated_post = post_request.model_dump(exclude_unset=True)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atleast one field should be provided"
        )

    for key,value in updated_post.items():
        setattr(post_model, key, value)

    db.add(post_model)
    db.commit()
    db.refresh(post_model)

    return PostResponse(
        id=post_model.id,
        title=post_model.title,
        description=post_model.description,
        owner=schemas.User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email
        ),
        created_at=post_model.created_at,
        updated_at=post_model.updated_at,
        message="Post updated",
    )

@router.delete("/{post_id}",response_model=PostResponse,status_code=status.HTTP_200_OK)
async def delete_user_post(user:user_dependency,db:db_dependency,post_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized"
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    post_model = db.query(Post).filter(Post.id == post_id).first()
    if post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if post_model.owner_id != user_model.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this post"
        )

    db.delete(post_model)
    db.commit()
    db.refresh(post_model)
    return PostResponse(
        id=post_model.id,
        title=post_model.title,
        description=post_model.description,
        owner=schemas.User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email
        ),
        created_at=post_model.created_at,
        updated_at=post_model.updated_at,
        message="Post deleted",
    )