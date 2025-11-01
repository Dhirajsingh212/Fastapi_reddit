from fastapi.security import OAuth2PasswordRequestForm
from database.db import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

from utils.auth_util import get_current_user

db_dependency = Annotated[Session, Depends(get_db)]
form_data_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
user_dependency = Annotated[dict,Depends(get_current_user)]