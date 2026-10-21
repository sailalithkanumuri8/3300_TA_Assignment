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
    """Reset task data before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])
    app_module.next_id = 3


def test_index(client):
    """Render the task tracker page and priority controls."""
    response = client.get('/')

    assert response.status_code == 200
    assert b"Task Tracker" in response.data
    assert b'id="task-priority"' in response.data
    assert b'value="Low"' in response.data
    assert b'value="Medium"' in response.data
    assert b'value="High"' in response.data


def test_get_tasks(client):
    """Return all tasks and add defaults to legacy tasks."""
    response = client.get('/api/tasks')

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)
    assert all(task['priority'] == 'Medium' for task in tasks)


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_valid_priorities(client, priority):
    """Create tasks with each supported priority."""
    response = client.post(
        '/api/tasks',
        json={"title": f"{priority} task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == priority

    get_response = client.get('/api/tasks')
    created_task = get_response.get_json()[-1]
    assert created_task['priority'] == priority


def test_add_task_priority_is_case_insensitive_and_normalized(client):
    """Normalize supported priorities before storing them."""
    response = client.post(
        '/api/tasks',
        json={"title": "Normalized task", "priority": " high "}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'High'


@pytest.mark.parametrize('priority', [None, '', 'Urgent', 1])
def test_add_task_invalid_priority_defaults_to_medium(client, priority):
    """Use Medium when a submitted priority is invalid."""
    response = client.post(
        '/api/tasks',
        json={"title": "Default priority task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_missing_priority_defaults_to_medium(client):
    """Use Medium when the priority field is omitted."""
    response = client.post('/api/tasks', json={"title": "Default task"})

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_success(client):
    """Create a task and return its persisted fields."""
    response = client.post('/api/tasks', json={"title": "Test new task"})

    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == "Test new task"
    assert data['priority'] == 'Medium'

    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


def test_add_task_missing_title(client):
    """Reject task creation requests without a title."""
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
