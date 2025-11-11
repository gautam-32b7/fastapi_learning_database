from fastapi import FastAPI, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field

from database import engine, session_local
import models
from models import Todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


# Provide a database session and ensures it's closed after use
def get_session():
    session = session_local()
    try:
        yield session
    finally:
        session.close()


# Defines a dependency that provides a database session to routes
session_dep = Annotated[Session, Depends(get_session)]


# Pydantic model for validating todo item data in requests
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


# Retrieve all todo items from the database
@app.get('/', status_code=status.HTTP_200_OK)
async def read_all(session: session_dep):
    return session.query(Todos).all()


# Retrieve a single todo item by its ID
@app.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def read_todo(session: session_dep, todo_id: int = Path(gt=0)):
    todo = session.query(Todos).filter(Todos.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=404, detail='Todo not found')


# Create a new todo item in the database
@app.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(session: session_dep, todo_request: TodoRequest):
    todo = Todos(**todo_request.model_dump())
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


# Update an existing todo item by its ID
@app.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(session: session_dep, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo = session.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    todo.title = todo_request.title
    todo.description = todo_request.description
    todo.priority = todo_request.priority
    todo.complete = todo_request.complete
    session.add(todo)
    session.commit()


# Delete a todo item by its ID
@app.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(session: session_dep, todo_id: int = Path(gt=0)):
    todo = session.query(Todos).filter(Todos.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    session.query(Todos).filter(Todos.id == todo_id).delete()
    session.commit()
