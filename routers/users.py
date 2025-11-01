from datetime import timedelta
from fastapi import APIRouter, HTTPException,Response

from database.models import User
from dependency import db_dependency, form_data_dependency, user_dependency
from schemas import Token, UserRequest, UserResponse, UserUpdateRequest
from starlette import status
from utils.auth_util import authenticate_user, create_access_token, password_hash

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse,status_code=status.HTTP_201_CREATED)
async def create_new_user(db: db_dependency, user_request: UserRequest):
    if (
        db.query(User).filter(User.username == user_request.username).first()
        is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username already exists"
        )

    user_model = User(
        username=user_request.username,
        email=user_request.email,
        password_hash=password_hash.hash(user_request.password),
        active=True,
    )

    db.add(user_model)
    db.commit()
    db.refresh(user_model)

    return UserResponse(
        message="User created successfully",
        id=user_model.id,
        username=user_model.username,
        email=user_model.email,
        createdAt=user_model.created_at,
        updatedAt=user_model.updated_at,
    )


@router.post("/token", response_model=Token, status_code=status.HTTP_200_OK)
async def authenticate_user_and_gen_token(
    form_data: form_data_dependency, db: db_dependency,response:Response
):
    user = authenticate_user(form_data.username, form_data.password, db)

    if isinstance(user, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=user)
    else:
        token = create_access_token(user.username, user.id, timedelta(minutes=20))
        response.set_cookie(key="token", value=token, httponly=True)
        return {"access_token": token, "token_type": "bearer"}


@router.get("/",response_model=UserResponse,status_code=status.HTTP_200_OK)
async def get_user_detail(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unauthorized",
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(
        id=user_model.id,
        username=user_model.username,
        email=user_model.email,
        createdAt=user_model.created_at,
        updatedAt=user_model.updated_at,
    )

@router.put("/",response_model=UserResponse,status_code=status.HTTP_200_OK)
async def update_user_detail(user:user_dependency,db:db_dependency,user_request: UserUpdateRequest):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unauthorized",
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    updated_user = user_request.model_dump(exclude_unset=True)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Atleast one field is required",
        )
    for key,value in updated_user.items():
        setattr(user_model, key, value)

    db.commit()
    db.refresh(user_model)

    return UserResponse(
        id=user_model.id,
        username=user_model.username,
        email=user_model.email,
        createdAt=user_model.created_at,
        updatedAt=user_model.updated_at,
        message="user updated successfully"
    )
@router.delete("/",response_model=UserResponse,status_code=status.HTTP_200_OK)
async def delete_user(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unauthorized",
        )

    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    db.query(User).filter(User.id == user.get('id')).delete()
    db.commit()

    return UserResponse(
        message="Successfully deleted",
        id=user_model.id,
        username=user_model.username,
        email=user_model.email,
        createdAt=user_model.created_at,
        updatedAt=user_model.updated_at,
    )