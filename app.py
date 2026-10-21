from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

PRIORITIES = ("Low", "Medium", "High")
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report"},
    {"id": 2, "title": "Project-2 MMFs"}
]
next_id = 3


def normalize_task(task):
    """Ensure a task has the default priority when it is missing."""
    if not task.get("priority"):
        task["priority"] = DEFAULT_PRIORITY
    return task


@app.route('/')
def index():
    """Render the task tracker page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Return all tasks with normalized priorities."""
    for task in tasks:
        normalize_task(task)
    return jsonify(tasks)


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Create a task with a validated priority."""
    global next_id

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        data = request.form.to_dict()

    if not data or not data.get('title'):
        return jsonify({"error": "Title is required"}), 400

    priority = data.get("priority") or DEFAULT_PRIORITY
    if priority not in PRIORITIES:
        return jsonify({"error": "Invalid priority"}), 400

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
    """Delete the task matching the supplied identifier."""
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return jsonify({"result": "success"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
