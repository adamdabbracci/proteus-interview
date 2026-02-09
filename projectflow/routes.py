"""REST API endpoint definitions for ProjectFlow.

All routes are registered under the ``/api`` URL prefix via a Flask
Blueprint. Route handlers access the shared ``ProjectStore`` through
``current_app.store``, which is initialized by the application factory.
"""

from flask import Blueprint, current_app, jsonify, request

api = Blueprint("api", __name__)


def _store():
    """Return the ProjectStore instance attached to the current app."""
    return current_app.store


# ----------------------------------------------------------------------
# Project endpoints
# ----------------------------------------------------------------------


@api.route("/projects", methods=["POST"])
def create_project():
    """Create a new project.

    Expects a JSON body with a required ``name`` field and an optional
    ``description`` field.

    Returns:
        201: The created project object.
        400: If the ``name`` field is missing.
    """
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Project name is required"}), 400

    project = _store().create_project(
        name=data["name"],
        description=data.get("description", ""),
    )
    return jsonify(project.to_dict()), 201


@api.route("/projects", methods=["GET"])
def list_projects():
    """List all projects.

    Returns:
        200: Array of project objects.
    """
    projects = _store().list_projects()
    return jsonify([p.to_dict() for p in projects]), 200


@api.route("/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    """Retrieve a single project by ID.

    Returns:
        200: The project object with all tasks.
        404: If no project matches the given ID.
    """
    project = _store().get_project(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(project.to_dict()), 200


@api.route("/projects/<project_id>", methods=["DELETE"])
def delete_project(project_id):
    """Delete a project by ID.

    Returns:
        204: Project successfully deleted (no body).
        404: If no project matches the given ID.
    """
    if _store().delete_project(project_id):
        return "", 204
    return jsonify({"error": "Project not found"}), 404


@api.route("/projects/<project_id>/clone", methods=["POST"])
def clone_project(project_id):
    """Clone a project as a reusable template.

    Creates an independent copy of the project and all its tasks.
    The clone receives a new unique ID and the name provided in the
    request body.

    Expects a JSON body with a required ``name`` field.

    Returns:
        201: The newly cloned project object.
        400: If the ``name`` field is missing.
        404: If the source project is not found.
    """
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "Clone name is required"}), 400

    cloned = _store().clone_project(project_id, data["name"])
    if cloned is None:
        return jsonify({"error": "Source project not found"}), 404
    return jsonify(cloned.to_dict()), 201


# ----------------------------------------------------------------------
# Task endpoints
# ----------------------------------------------------------------------


@api.route("/projects/<project_id>/tasks", methods=["POST"])
def add_task(project_id):
    """Add a new task to a project.

    Expects a JSON body with a required ``title`` field and optional
    ``description``, ``assignee``, and ``labels`` fields.

    Returns:
        201: The created task object.
        400: If the ``title`` field is missing.
        404: If the project is not found.
    """
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "Task title is required"}), 400

    task = _store().add_task_to_project(
        project_id=project_id,
        title=data["title"],
        description=data.get("description", ""),
        assignee=data.get("assignee"),
        labels=data.get("labels", []),
    )
    if task is None:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(task.to_dict()), 201


@api.route("/projects/<project_id>/tasks/<task_id>", methods=["PATCH"])
def update_task(project_id, task_id):
    """Update one or more fields on an existing task.

    Supports partial updates — include only the fields you wish to
    change in the JSON body. Valid fields: ``title``, ``description``,
    ``status``, ``assignee``, ``labels``.

    Returns:
        200: The updated task object.
        400: If the request body is empty.
        404: If the project or task is not found.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    task = _store().update_task(project_id, task_id, **data)
    if task is None:
        return jsonify({"error": "Project or task not found"}), 404
    return jsonify(task.to_dict()), 200
