document.addEventListener('DOMContentLoaded', fetchTasks);

const defaultPriority = 'Medium';

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');
        const taskDetails = document.createElement('div');
        const title = document.createElement('span');
        const priority = document.createElement('span');
        const deleteButton = document.createElement('button');

        title.textContent = task.title;
        priority.textContent = task.priority || defaultPriority;
        priority.className = 'priority-indicator';
        priority.classList.add(
            `priority-${(task.priority || defaultPriority).toLowerCase()}`
        );
        deleteButton.textContent = 'Delete';
        deleteButton.className = 'delete-btn';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        taskDetails.className = 'task-details';
        taskDetails.appendChild(title);
        taskDetails.appendChild(priority);
        li.appendChild(taskDetails);
        li.appendChild(deleteButton);
        taskList.appendChild(li);
    });
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();
    const priority = priorityInput.value || defaultPriority;

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, priority })
    });

    titleInput.value = '';
    priorityInput.value = defaultPriority;
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
