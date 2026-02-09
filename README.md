# ProjectFlow

A lightweight project management REST API built with Flask. ProjectFlow lets teams create projects, manage tasks, and clone projects as reusable templates for recurring workflows.

## Features

- **Project Management** — Create, list, view, and delete projects
- **Task Tracking** — Add tasks with titles, descriptions, assignees, and labels
- **Task Updates** — Change status, reassign ownership, update labels
- **Project Cloning** — Duplicate a project and all its tasks as a starting template

## Setup

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)

### Installation

```bash
# Create a virtual environment and install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Running the Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`.

### Running Tests

```bash
pytest tests/
```

## API Reference

### Projects

| Method   | Endpoint                    | Description          |
|----------|-----------------------------|----------------------|
| `POST`   | `/api/projects`             | Create a new project |
| `GET`    | `/api/projects`             | List all projects    |
| `GET`    | `/api/projects/:id`         | Get a project by ID  |
| `DELETE` | `/api/projects/:id`         | Delete a project     |
| `POST`   | `/api/projects/:id/clone`   | Clone a project      |

### Tasks

| Method  | Endpoint                                | Description      |
|---------|-----------------------------------------|------------------|
| `POST`  | `/api/projects/:id/tasks`               | Add a task       |
| `PATCH` | `/api/projects/:id/tasks/:task_id`      | Update a task    |

## Example Usage

**Create a project:**

```bash
curl -X POST http://localhost:5000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Q1 Sprint", "description": "First quarter deliverables"}'
```

**Add tasks:**

```bash
curl -X POST http://localhost:5000/api/projects/<project_id>/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Set up CI pipeline", "assignee": "alice", "labels": ["infra"]}'
```

**Clone a project:**

```bash
curl -X POST http://localhost:5000/api/projects/<project_id>/clone \
  -H "Content-Type: application/json" \
  -d '{"name": "Q2 Sprint"}'
```

**Update a task:**

```bash
curl -X PATCH http://localhost:5000/api/projects/<project_id>/tasks/<task_id> \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

## Architecture

```
projectflow/
├── __init__.py         # Package init and app export
├── app.py              # Flask application factory
├── models.py           # Task and Project data models
├── routes.py           # REST API endpoint definitions
└── services.py         # Business logic and in-memory storage
```

Data is stored in memory and resets when the server restarts. This is intentional — ProjectFlow is designed as a lightweight coordination tool, not a database-backed production system.
