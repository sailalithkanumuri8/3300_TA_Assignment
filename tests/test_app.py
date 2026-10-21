import pytest

import app as app_module
from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset task data and IDs before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])
    app_module.next_id = 3


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Return all tasks with a default priority."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


def test_add_task_success(client):
    """Create a task without priority using Medium by default."""
    response = client.post('/api/tasks', json={"title": "Test new task"})
    assert response.status_code == 201
    assert response.get_json()['title'] == "Test new task"
    assert response.get_json()['priority'] == "Medium"

    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_with_each_priority(client, priority):
    """Create and retrieve a task for every supported priority."""
    response = client.post(
        '/api/tasks',
        json={"title": f"{priority} task", "priority": priority}
    )

    assert response.status_code == 201
    created_task = response.get_json()
    assert created_task['priority'] == priority

    get_response = client.get('/api/tasks')
    returned_task = get_response.get_json()[-1]
    assert returned_task['priority'] == priority


def test_empty_priority_defaults_to_medium(client):
    """Treat an empty priority as Medium."""
    response = client.post(
        '/api/tasks',
        json={"title": "Task with empty priority", "priority": ""}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_invalid_priority_is_rejected(client):
    """Reject priorities outside the supported values."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid priority task", "priority": "Urgent"}
    )

    assert response.status_code == 400
    assert 'error' in response.get_json()
    assert len(tasks) == 2


def test_existing_task_without_priority_is_serialized_as_medium(client):
    """Serialize legacy tasks without priority as Medium."""
    tasks.append({"id": 3, "title": "Legacy task"})

    response = client.get('/api/tasks')
    legacy_task = response.get_json()[-1]

    assert legacy_task['title'] == 'Legacy task'
    assert legacy_task['priority'] == 'Medium'


def test_add_task_missing_title(client):
    """Reject task creation when the title is missing."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()

    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200
    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
