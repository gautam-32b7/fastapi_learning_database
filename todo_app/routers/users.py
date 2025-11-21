from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from passlib.context import CryptContext

from database import session_local
from models import Users
from .auth import get_current_user

router = APIRouter(
    prefix='/users',
    tags=['users']
)


# Provide a database session and ensures it's closed after use
def get_session():
    session = session_local()
    try:
        yield session
    finally:
        session.close()


# Defines a dependency that provides a database session to routes
session_dep = Annotated[Session, Depends(get_session)]

# Defines a dependency that provides JWT authentication to routes
user_dep = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Pydantic model for user password verification
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


# Comment
@router.get('/', status_code=status.HTTP_200_OK)
async def get_user(user: user_dep, session: session_dep):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication fail')
    return session.query(Users).filter(Users.id == user.get('id')).first()


# Comment
@router.put('/password-change', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dep, session: session_dep, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')
    user_model = session.query(Users).filter(
        Users.id == user.get('id')).first()
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    user_model.hashed_password = bcrypt_context.hash(
        user_verification.new_password)
    session.add(user_model)
    session.commit()
