from fastapi.testclient import TestClient
from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from database import Base
from routers.todos import get_session, get_current_user
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
    return {'username': 'john_doe', id: 3, 'user_role': 'user'}


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = overrides_get_current_user

client = TestClient(app)


def test_read_all_authenticated():
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
