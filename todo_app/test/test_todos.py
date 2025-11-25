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

    # Run this snippet after the test executed
    yield todo
    with engine.connect() as connection:
        connection.execute(text('DELETE FROM todos;'))
        connection.commit()


def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'title': 'Learn to code', 'description': 'Lorem ipsum dolor', 'priority': 5, 'complete': False, 'owner_id': 3, 'id': 1}]


def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'Learn to code', 'description': 'Lorem ipsum dolor',
                               'priority': 5, 'complete': False, 'owner_id': 3, 'id': 1}


def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
