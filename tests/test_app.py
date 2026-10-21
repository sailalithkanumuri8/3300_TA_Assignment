from pathlib import Path

import pytest

import app as app_module
from app import app, tasks


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset tasks and IDs before each test."""
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
    """Return all existing tasks with default priorities."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == 'Medium' for task in data)


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_priority(client, priority):
    """Create and retrieve a task with each supported priority."""
    response = client.post(
        '/api/tasks',
        json={'title': f'{priority} task', 'priority': priority}
    )

    assert response.status_code == 201
    created_task = response.get_json()
    assert created_task['priority'] == priority

    get_response = client.get('/api/tasks')
    retrieved_task = next(
        task for task in get_response.get_json()
        if task['id'] == created_task['id']
    )
    assert retrieved_task['priority'] == priority


def test_add_task_missing_priority_defaults_to_medium(client):
    """Default a task without a priority to Medium."""
    response = client.post('/api/tasks', json={'title': 'Default task'})

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


def test_add_task_empty_priority_defaults_to_medium(client):
    """Default a task with an empty priority to Medium."""
    response = client.post(
        '/api/tasks',
        json={'title': 'Empty priority task', 'priority': ''}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == 'Medium'


@pytest.mark.parametrize('priority', ['Urgent', 'low', 'HIGH'])
def test_add_task_rejects_invalid_priority(client, priority):
    """Reject priorities outside the supported values."""
    response = client.post(
        '/api/tasks',
        json={'title': 'Invalid priority task', 'priority': priority}
    )

    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_legacy_tasks_receive_medium_priority(client):
    """Resolve missing priorities on legacy tasks returned by the API."""
    tasks.append({'id': 3, 'title': 'Legacy task'})

    response = client.get('/api/tasks')
    legacy_task = next(
        task for task in response.get_json() if task['id'] == 3
    )

    assert legacy_task['priority'] == 'Medium'
    assert tasks[2]['priority'] == 'Medium'


def test_frontend_priority_controls_and_rendering():
    """Verify the frontend submits and renders task priorities."""
    template = Path('templates/index.html').read_text()
    script = Path('static/app.js').read_text()

    assert 'id="task-priority"' in template
    assert 'value="Low"' in template
    assert 'value="Medium"' in template
    assert 'value="High"' in template
    assert 'priorityInput.value' in script
    assert 'priority.textContent = resolvedPriority' in script


def test_add_task_success(client):
    """Create a task without explicitly setting its priority."""
    response = client.post('/api/tasks', json={'title': 'Test new task'})
    assert response.status_code == 201
    assert response.get_json()['title'] == 'Test new task'
    assert response.get_json()['priority'] == 'Medium'
    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


def test_add_task_missing_title(client):
    """Reject task creation when the title is missing."""
    response = client.post('/api/tasks', json={'wrong_key': 'value'})
    assert response.status_code == 400
    assert 'error' in response.get_json()
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
