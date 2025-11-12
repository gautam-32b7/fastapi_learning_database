from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session

from database import session_local
from models import Users

router = APIRouter()
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# Provide a database session and ensures it's closed after use
def get_session():
    session = session_local()
    try:
        yield session
    finally:
        session.close()


# Defines a dependency that provides a database session to routes
session_dep = Annotated[Session, Depends(get_session)]


# Pydantic model for validating user data in requests
class CreateUserRequest(BaseModel):
    useranme: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


# Create a new user in the database
@router.post('/auth', status_code=status.HTTP_201_CREATED)
async def create_user(session: session_dep, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.useranme,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    session.add(create_user_model)
    session.commit()
