from cryptography.x509 import random_serial_number
from fastapi import APIRouter, Path, HTTPException
from pyexpat.errors import messages
from sqlalchemy.orm import joinedload
from starlette import status
from typing import List
import schemas
from database import db
from database.models import Post, Comment, User
from schemas import CommentRequest, CommentResponse, CommentWithUserDetails, CommentUpdateRequest
from dependency import user_dependency,db_dependency

router = APIRouter(
    prefix="/comment",
    tags=["comment"]
)

@router.post("/{post_id}",response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def create_comment(user:user_dependency,db:db_dependency,comment_request:CommentRequest,post_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    post_model = (db
                  .query(Post)
                  .filter(Post.id == post_id)
                  .options(joinedload(Post.owner))
                  .first())

    if post_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    comment_model = Comment(
        comment=comment_request.comment,
        post_id=post_model.id,
        owner_id=user_model.id
    )

    db.add(comment_model)
    db.commit()
    db.refresh(comment_model)

    return CommentResponse(
        id=comment_model.id,
        comment=comment_model.comment,
        created_at=comment_model.created_at,
        updated_at=comment_model.updated_at,
        owner=schemas.User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
        ),
        post=schemas.PostResponse(
            id=post_model.id,
            title=post_model.title,
            description=post_model.description,
            created_at=post_model.created_at,
            updated_at=post_model.updated_at,
            owner=schemas.User(
                id=post_model.owner.id,
                username=post_model.owner.username,
                email=post_model.owner.email,
            )
        )
    )

@router.get("/{post_id}",response_model=List[CommentWithUserDetails],status_code=status.HTTP_200_OK)
async def get_all_comments_by_post(user:user_dependency,db:db_dependency,post_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
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

    comments = (db
                .query(Comment)
                .filter(Comment.post_id == post_model.id)
                .options(joinedload(Comment.owner))
                .all())

    return comments

@router.put("/{comment_id}",response_model=CommentWithUserDetails,status_code=status.HTTP_200_OK)
async def update_comment_details(user:user_dependency,db:db_dependency,comment_request:CommentUpdateRequest,comment_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    comment_model = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment_model.owner_id != user_model.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this comment"
        )

    updated_comment = comment_request.model_dump(exclude_unset=True)
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atleast one Field is required"
        )

    for key,value in updated_comment.items():
        setattr(comment_model, key, value)

    db.add(comment_model)
    db.commit()
    db.refresh(comment_model)

    return CommentWithUserDetails(
        id=comment_model.id,
        comment=comment_model.comment,
        owner=schemas.User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
        ),
        message="Comment updated successfully"
    )

@router.delete("/{comment_id}",response_model=CommentWithUserDetails,status_code=status.HTTP_200_OK)
async def delete_comment(user:user_dependency,db:db_dependency,comment_id:int = Path(gt=0)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    comment_model = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if comment_model.owner_id != user_model.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this comment"
        )

    db.delete(comment_model)
    db.commit()

    return CommentWithUserDetails(
        id=comment_model.id,
        comment=comment_model.comment,
        owner=schemas.User(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
        ),
        message="Deleted comment"
    )
