from fastapi import status
from fastapi.testclient import TestClient

from routers.admin import get_session, get_current_user
from models import Todos
from .utils import *
from main import app

app.dependency_overrides[get_session] = override_get_session
app.dependency_overrides[get_current_user] = overrides_get_current_user

client = TestClient(app)


# Test: authenticated admin should see all todos
def test_admin_read_all_authenticated(test_todo):
    response = client.get('/admin/todo')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'title': 'Learn to code', 'description': 'Lorem ipsum dolor',
                               'priority': 5, 'complete': False, 'owner_id': 6, 'id': 1}]


# Test: admin delete a todo
def test_admin_delete_todo(test_todo):
    response = client.delete('/admin/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = testing_session_local()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


# Test: delete a non-existing todo should return 404
def test_admin_delete_todo_not_found(test_todo):
    response = client.delete('/admin/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
