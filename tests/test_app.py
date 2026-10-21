import pytest

from app import app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task data before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Return all tasks from the task endpoint."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


def test_get_tasks_defaults_missing_priority_to_medium(client):
    """Use Medium for existing tasks without a priority."""
    response = client.get('/api/tasks')
    data = response.get_json()

    assert all(task['priority'] == 'Medium' for task in data)


def test_add_task_success(client):
    """Create a task without priority using the default value."""
    response = client.post('/api/tasks', json={"title": "Test new task"})
    assert response.status_code == 201
    created_task = response.get_json()
    assert created_task['title'] == "Test new task"
    assert created_task['priority'] == 'Medium'

    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


@pytest.mark.parametrize('priority', ['Low', 'Medium', 'High'])
def test_add_task_accepts_supported_priorities(client, priority):
    """Create tasks with each supported priority value."""
    response = client.post(
        '/api/tasks',
        json={"title": "Prioritized task", "priority": priority}
    )

    assert response.status_code == 201
    assert response.get_json()['priority'] == priority


def test_add_task_rejects_invalid_priority(client):
    """Reject priorities outside the supported set."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid task", "priority": "Urgent"}
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid priority"


def test_priority_persists_in_get_response(client):
    """Return a newly created priority in subsequent task responses."""
    create_response = client.post(
        '/api/tasks',
        json={"title": "High priority task", "priority": "High"}
    )
    created_task = create_response.get_json()

    get_response = client.get('/api/tasks')
    matching_tasks = [
        task for task in get_response.get_json()
        if task['id'] == created_task['id']
    ]

    assert len(matching_tasks) == 1
    assert matching_tasks[0]['priority'] == 'High'


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
