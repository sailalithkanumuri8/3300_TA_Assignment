from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

SUPPORTED_PRIORITIES = ("Low", "Medium", "High")
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report"},
    {"id": 2, "title": "Project-2 MMFs"}
]
next_id = 3


def normalize_priority(priority):
    """Return a normalized priority or None for an invalid value."""
    if priority is None:
        return DEFAULT_PRIORITY

    if isinstance(priority, str) and not priority.strip():
        return DEFAULT_PRIORITY

    if priority not in SUPPORTED_PRIORITIES:
        return None

    return priority


def serialize_task(task):
    """Return a task with a priority for API responses."""
    serialized_task = dict(task)
    priority = normalize_priority(serialized_task.get("priority"))
    serialized_task["priority"] = priority or DEFAULT_PRIORITY
    return serialized_task


@app.route('/')
def index():
    """Render the task tracker page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks with normalized priorities."""
    return jsonify([serialize_task(task) for task in tasks])


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create and return a task with a validated priority."""
    global next_id
    data = request.get_json()

    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    priority = normalize_priority(data.get("priority"))
    if priority is None:
        return jsonify({
            "error": "Priority must be Low, Medium, or High"
        }), 400

    new_task = {
        "id": next_id,
        "title": data['title'],
        "priority": priority
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete the task with the specified ID."""
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return jsonify({"result": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
