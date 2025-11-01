from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Dict
from fastapi import Cookie, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database.models import User
from jose import jwt, JWTError
from starlette import status
from pwdlib import PasswordHash
from config.config import setting

password_hash = PasswordHash.recommended()
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="users/token")

SECRET_KEY = setting.JWT_SECRET
ALGORITHM = setting.JWT_ALGORITHM


def create_access_token(username: str, user_id: str, expires_delta: timedelta):
    encode: Dict[Any, Any] = {"sub": username, "id": user_id}

    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})

    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str, db):
    user_model = db.query(User).filter(User.username == username).first()
    if not user_model:
        return "User not found"

    if not password_hash.verify(password, user_model.password_hash):
        return "Incorrect password"

    return user_model

async def get_current_user(token:Annotated[str, Cookie()]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )