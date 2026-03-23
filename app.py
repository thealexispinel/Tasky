from flask import Flask, render_template, request, jsonify, Response
from ics import Calendar, Event
from datetime import datetime, timedelta 
import json
import requests


app = Flask(__name__)

# Función leer tareas

def load_tasks():
    try:
        with open('tasks.json', 'r') as file:
            return json.load(file)
    except:
        return[]
    
# Función guardar tareas
    
def save_tasks(tasks):
    with open('tasks.json', 'w') as file:
        json.dump(tasks, file)

# Ruta Principal

@app.route('/')
def index():
    return render_template('index.html')

#Función Obtener Tarea

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(load_tasks())

# Función IA - Modelo phi3

def get_priority(text):
    prompt = f"""
    Clasifica esta tarea en prioridad: alta, media o baja.

    Tarea: "{text}"

    Responde SOLO una palabra.
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3",
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()["response"].strip().lower()

        if "alta" in result:
            return "alta"
        elif "media" in result:
            return "media"
        else:
            return "baja"

    except Exception as e:
        print("Error IA:", e)
        return "media"

# Función Agregar Tarea

@app.route('/tasks', methods=['POST'])
def add_task():
    tasks = load_tasks()
    data = request.json
    print("Tarea Agregada:", data)
    priority = get_priority(data['text'])

    new_task = {
        "id": len(tasks) + 1,
        "text": data['text'],
        "details": data ['details'],
        "completed": False,
        "priority": priority,
        "date": data.get('date')
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return jsonify (new_task)

# Función Completar tarea

@app.route('/tasks/<int:id>', methods=['PUT'])
def complete_task(id):
    tasks = load_tasks()

    for task in tasks:
        if task['id'] == id:
            task['completed'] = not task['completed']

    save_tasks(tasks)
    return jsonify({"message": "update"})

# Función eliminar tarea

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_tasks(id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != id]

    save_tasks(tasks)
    return jsonify({"message": "deleted"})

# Función Guardado en el calendario

@app.route('/export/<int:id>')
def export_task(id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == id), None)

    if not task or not task.get('date'):
        return {"error": "Tarea sin fecha"}, 400

    date_obj = datetime.strptime(task['date'], "%Y-%m-%d")

    start = date_obj.strftime("%Y%m%dT090000")
    end = (date_obj + timedelta(hours=1)).strftime("%Y%m%dT100000")

    content = f"""BEGIN:VCALENDAR
    VERSION:2.0
    BEGIN:VEVENT
    SUMMARY:{task['text']}
    DESCRIPTION:Prioridad: {task.get('priority', 'media')}
    DTSTART:{start}
    DTEND:{end}
    END:VEVENT
    END:VCALENDAR
    """

    return Response(
        content,
        mimetype="text/calendar",
        headers={"Content-Disposition": f"attachment;filename=task_{id}.ics"}
    )

if __name__ == '__main__':
    app.run(debug = True)