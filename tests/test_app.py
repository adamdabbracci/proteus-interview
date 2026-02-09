"""Basic test suite for ProjectFlow API.

Covers the core CRUD operations and verifies that the API contract
is stable. Run with: ``pytest tests/``
"""

import json

import pytest

from projectflow import create_app


@pytest.fixture()
def client():
    """Create a Flask test client with a fresh application instance."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def _post_json(client, url, data):
    """Helper: send a POST request with a JSON body."""
    return client.post(url, data=json.dumps(data), content_type="application/json")


def _patch_json(client, url, data):
    """Helper: send a PATCH request with a JSON body."""
    return client.patch(url, data=json.dumps(data), content_type="application/json")


# ------------------------------------------------------------------
# Project tests
# ------------------------------------------------------------------


class TestProjects:
    """Tests for project CRUD operations."""

    def test_create_project(self, client):
        resp = _post_json(client, "/api/projects", {"name": "Test Project"})
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["name"] == "Test Project"
        assert "id" in body

    def test_create_project_missing_name(self, client):
        resp = _post_json(client, "/api/projects", {})
        assert resp.status_code == 400

    def test_list_projects(self, client):
        _post_json(client, "/api/projects", {"name": "A"})
        _post_json(client, "/api/projects", {"name": "B"})
        resp = client.get("/api/projects")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2

    def test_get_project(self, client):
        create_resp = _post_json(client, "/api/projects", {"name": "P"})
        pid = create_resp.get_json()["id"]
        resp = client.get(f"/api/projects/{pid}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "P"

    def test_get_project_not_found(self, client):
        resp = client.get("/api/projects/nonexistent")
        assert resp.status_code == 404

    def test_delete_project(self, client):
        create_resp = _post_json(client, "/api/projects", {"name": "Temp"})
        pid = create_resp.get_json()["id"]
        resp = client.delete(f"/api/projects/{pid}")
        assert resp.status_code == 204

    def test_delete_project_not_found(self, client):
        resp = client.delete("/api/projects/nonexistent")
        assert resp.status_code == 404


# ------------------------------------------------------------------
# Task tests
# ------------------------------------------------------------------


class TestTasks:
    """Tests for task management operations."""

    def _create_project(self, client, name="My Project"):
        resp = _post_json(client, "/api/projects", {"name": name})
        return resp.get_json()["id"]

    def test_add_task(self, client):
        pid = self._create_project(client)
        resp = _post_json(
            client,
            f"/api/projects/{pid}/tasks",
            {"title": "Do something", "labels": ["urgent"]},
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["title"] == "Do something"
        assert body["status"] == "todo"
        assert body["labels"] == ["urgent"]

    def test_add_task_missing_title(self, client):
        pid = self._create_project(client)
        resp = _post_json(client, f"/api/projects/{pid}/tasks", {})
        assert resp.status_code == 400

    def test_update_task_status(self, client):
        pid = self._create_project(client)
        task_resp = _post_json(
            client, f"/api/projects/{pid}/tasks", {"title": "Task 1"}
        )
        tid = task_resp.get_json()["id"]
        resp = _patch_json(
            client, f"/api/projects/{pid}/tasks/{tid}", {"status": "done"}
        )
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "done"

    def test_update_task_not_found(self, client):
        pid = self._create_project(client)
        resp = _patch_json(
            client, f"/api/projects/{pid}/tasks/fake-id", {"status": "done"}
        )
        assert resp.status_code == 404


# ------------------------------------------------------------------
# Clone tests
# ------------------------------------------------------------------


class TestClone:
    """Tests for project cloning."""

    def _create_project_with_tasks(self, client):
        resp = _post_json(
            client,
            "/api/projects",
            {"name": "Template", "description": "A reusable template"},
        )
        pid = resp.get_json()["id"]
        _post_json(client, f"/api/projects/{pid}/tasks", {"title": "Task A"})
        _post_json(client, f"/api/projects/{pid}/tasks", {"title": "Task B"})
        return pid

    def test_clone_creates_new_project(self, client):
        pid = self._create_project_with_tasks(client)
        resp = _post_json(
            client, f"/api/projects/{pid}/clone", {"name": "Clone"}
        )
        assert resp.status_code == 201
        body = resp.get_json()
        assert body["name"] == "Clone"
        assert body["id"] != pid
        assert len(body["tasks"]) == 2

    def test_clone_not_found(self, client):
        resp = _post_json(
            client, "/api/projects/nonexistent/clone", {"name": "X"}
        )
        assert resp.status_code == 404

    def test_clone_missing_name(self, client):
        pid = self._create_project_with_tasks(client)
        resp = _post_json(client, f"/api/projects/{pid}/clone", {})
        assert resp.status_code == 400

    def test_adding_task_to_clone_does_not_affect_original(self, client):
        """Verify that adding a new task to a clone leaves the original
        project unchanged."""
        pid = self._create_project_with_tasks(client)
        clone_resp = _post_json(
            client, f"/api/projects/{pid}/clone", {"name": "My Clone"}
        )
        clone_id = clone_resp.get_json()["id"]

        # Add a task to the clone only
        _post_json(
            client, f"/api/projects/{clone_id}/tasks", {"title": "New task"}
        )

        # Original should still have exactly 2 tasks
        original = client.get(f"/api/projects/{pid}").get_json()
        assert len(original["tasks"]) == 2
