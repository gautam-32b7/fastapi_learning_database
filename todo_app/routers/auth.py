from fastapi import APIRouter, Depends
from pydantic import BaseModel
from starlette import status
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

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


# Authenticate a user by verifying the provided username and password
def authenticate_user(username: str, password: str, session):
    user = session.query(Users).filter(Users.username == username).first()
    print(user)
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return True


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


# Handle user login and return a successful or failure response based on authentication
@router.post('/token')
async def login_for_access_token(session: session_dep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        return 'Failed'
    return 'Successful'
