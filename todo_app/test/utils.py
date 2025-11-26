from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

import pytest

from database import Base
from models import Todos


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
