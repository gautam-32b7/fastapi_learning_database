from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import pytest

from database import Base
from routers.todos import get_session, get_current_user
from models import Todos
from main import app


SQLALCHEMY_DATABASE_URL = 'sqlite:///./test_db.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool
)

testing_session_local = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# Override get_session
def override_get_session():
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


# override get_user_user
def overrides_get_current_user():
    return {'username': 'john_doe', 'id': 3, 'user_role': 'user'}


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = overrides_get_current_user

client = TestClient(app)


# Fixture: create a test todo before each test and clean the table afterward
@pytest.fixture
def test_todo():
    todo = Todos(
        title='Learn to code',
        description='Lorem ipsum dolor',
        priority=5,
        complete=False,
        owner_id=3
    )

    db = testing_session_local()
    db.add(todo)
    db.commit()

    # After the test runs, delete all todos to reset the database
    yield todo
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))
        connection.commit()


# Test: authenticated user should see all their todos
def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'title': 'Learn to code', 'description': 'Lorem ipsum dolor', 'priority': 5, 'complete': False, 'owner_id': 3, 'id': 1}]


# Test: authenticated user should be able to read a specific todo by ID
def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'Learn to code', 'description': 'Lorem ipsum dolor',
                               'priority': 5, 'complete': False, 'owner_id': 3, 'id': 1}


# Test: reading a non-existing todo should return 404
def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


# Test: create a todo
def test_create_todo(test_todo):
    request_data = {
        'title': 'New todo',
        'description': 'Lorem ipsum dolor',
        'priority': 5,
        'complete': False
    }

    response = client.post('/todo', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = testing_session_local()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')
