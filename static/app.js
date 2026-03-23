async function loadTasks() {
    const res = await fetch('/tasks');
    const tasks = await res.json();

    const list = document.getElementById('taskList');
    list.innerHTML = '';

    tasks.forEach(task => {
        const li = document.createElement('li');

        li.innerHTML = `
            <span>
                ${task.text}
                <p>detalles: ${task.details}</p>
                <p>Completo: ${task.completed}</p>
                <p>Fecha: ${task.date}</p>
                <p>prioridad: ${task.priority}</p>
            </span>
            <button onclick="completeTask(${task.id})"> COMPLETAR </button>
            <button onclick="deleteTask(${task.id})"> ELIMINAR </button>
            <button onclick="exportTask(${task.id})"> EXPORTAR AL CALENDARIO </button>
        `;

        list.appendChild(li);
    });
}

async function addTask(){
    const input = document.getElementById('taskInput');
    const details = document.getElementById('detailsInput');
    const date = document.getElementById('dateInput');

    if(!input.value.trim()) return;

    await fetch('/tasks', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            text: input.value,
            details: details.value,
            date: date.value
        })
    });

    input.value = '';
    details.value = '';
    date.value = '';

    loadTasks();
}

async function completeTask(id) {
    await fetch(`/tasks/${id}`, {method: 'PUT'});
    loadTasks();
}

async function deleteTask(id) {
    await fetch(`/tasks/${id}`, {method: 'DELETE'});
    loadTasks();
}

function exportTask(id) {
    window.location.href = `/export/${id}`;
}

let color = 
    task.priority === 'alta' ? 'red':
    task.priority === 'media' ? 'orange': 'green';

loadTasks();