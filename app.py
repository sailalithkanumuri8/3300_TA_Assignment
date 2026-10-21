from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SUPPORTED_PRIORITIES = ("Low", "Medium", "High")
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report"},
    {"id": 2, "title": "Project-2 MMFs"}
]
next_id = 3


def normalize_priority(priority):
    """Return a supported priority or the default priority."""
    if not isinstance(priority, str):
        return DEFAULT_PRIORITY

    normalized_priority = priority.strip().lower()
    for supported_priority in SUPPORTED_PRIORITIES:
        if normalized_priority == supported_priority.lower():
            return supported_priority

    return DEFAULT_PRIORITY


def migrate_task_priorities():
    """Add the default priority to legacy tasks without one."""
    for task in tasks:
        task["priority"] = normalize_priority(task.get("priority"))


@app.route('/')
def index():
    """Render the task tracker page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks with normalized priorities."""
    migrate_task_priorities()
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a task with a validated priority."""
    global next_id
    data = request.get_json(silent=True)

    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    new_task = {
        "id": next_id,
        "title": data['title'],
        "priority": normalize_priority(data.get('priority'))
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete the task with the supplied identifier."""
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return jsonify({"result": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
