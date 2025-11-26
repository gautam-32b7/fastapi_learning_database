from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field

from database import session_local
from models import Todos
from .auth import get_current_user, get_session

router = APIRouter(
    prefix='/admin',
    tags=['admin']
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


# Retrieve all todo items from the database
@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(user: user_dep, session: session_dep):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication fail')
    return session.query(Todos).all()


# Delete a todo item by its ID
@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dep, session: session_dep, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication fail')
    todo_model = session.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    session.query(Todos).filter(Todos.id == todo_id).delete()
    session.commit()
