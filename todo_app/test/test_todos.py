from fastapi.testclient import TestClient
from fastapi import status

from routers.todos import get_session, get_current_user
from models import Todos
from main import app
from .utils import *


app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = overrides_get_current_user

client = TestClient(app)


# Test: authenticated user should see all their todos
def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {'title': 'Learn to code', 'description': 'Lorem ipsum dolor', 'priority': 5, 'complete': False, 'owner_id': 6, 'id': 1}]


# Test: authenticated user should be able to read a specific todo by ID
def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'title': 'Learn to code', 'description': 'Lorem ipsum dolor',
                               'priority': 5, 'complete': False, 'owner_id': 6, 'id': 1}


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


# Test: update an existing todo
def test_update_todo(test_todo):
    request_data = {
        'title': 'Change the title of the todo already saved!',
        'description': 'Lorem ipsum dolor',
        'priority': 5,
        'complete': False
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = testing_session_local()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get('title')


# Test: updating a non-existing todo should return 404 Not Found
def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Change the title of the todo already saved!',
        'description': 'Lorem ipsum dolor',
        'priority': 5,
        'complete': False
    }

    response = client.put('/todo/999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


# Test: delete an existing todo
def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = testing_session_local()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


# Test: delete non existing todo and should return 404 Not Found
def test_delete_todo_not_found(test_todo):
    response = client.delete('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
