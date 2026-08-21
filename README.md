# Full-Stack Task Manager with AI Summarization

A full-stack task management app with a Python/Django backend and a
vanilla-JavaScript kanban board on the front end. Paste raw meeting notes
into a task and it auto-generates a summary and action-item list using
Generative AI.

## Tech Stack
- **Backend:** Python, Django
- **Frontend:** JavaScript (drag-and-drop kanban board), HTML, CSS
- **Database:** MySQL in production / SQLite for local dev (toggle via env vars)
- **Gen AI:** OpenAI API for summarization (optional — extractive fallback works with zero API key)

## Features
- Multi-user task assignment (`ManyToMany` between `Task` and `User`) grouped under `Project` workspaces
- Kanban board (To Do / In Progress / Done) with drag-and-drop that persists via AJAX
- AI summarization: paste meeting notes → get a summary + action items, either inline while creating a task or via a standalone `/api/summarize/` endpoint
- Priority levels and due dates with visual badges
- Django admin panel for quick data management

## Setup

```bash
cd taskmanager
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# optional — enables real LLM-generated summaries
export OPENAI_API_KEY=sk-...

python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

Visit `http://localhost:8000`. Create a Project first (`/projects/new/`), then add tasks against it.

### Using MySQL instead of SQLite
```bash
export DB_ENGINE=django.db.backends.mysql
export DB_NAME=taskmanager
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
export DB_PORT=3306
pip install mysqlclient
python manage.py migrate
```

## API

| Endpoint              | Method | Description                                  |
|------------------------|--------|-----------------------------------------------|
| `/api/summarize/`      | POST   | `{"notes": "..."}` → `{"summary": "..."}`      |
| `/tasks/<id>/status/`  | POST   | `{"status": "in_progress"}` → updates task status (used by the kanban drag-drop) |

## Project Structure
```
taskmanager/
├── manage.py
├── taskmanager/           # project settings, urls, wsgi/asgi
└── tasks/                 # app: models, views, forms, AI summarizer
    ├── models.py           # Project, Task
    ├── views.py            # CRUD + kanban + summarize endpoint
    ├── ai_summarizer.py    # Gen AI summarization (OpenAI + extractive fallback)
    ├── templates/tasks/
    └── static/tasks/       # app.js (drag-drop), style.css
```
