"""Business logic and in-memory storage for ProjectFlow.

The ``ProjectStore`` class provides the main service layer, encapsulating
all CRUD operations, task management, and project cloning functionality.
Data lives in memory and does not persist across server restarts.
"""

from typing import Optional

from .models import Project, Task


class ProjectStore:
    """Thread-safe in-memory store for projects and their tasks.

    All public methods operate on a shared dictionary of Project objects
    keyed by project ID.
    """

    def __init__(self):
        self._projects: dict[str, Project] = {}

    # ------------------------------------------------------------------
    # Project CRUD
    # ------------------------------------------------------------------

    def create_project(self, name: str, description: str = "") -> Project:
        """Create a new empty project.

        Args:
            name: Human-readable project name.
            description: Optional project description.

        Returns:
            The newly created Project.
        """
        project = Project(name=name, description=description)
        self._projects[project.id] = project
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by its unique ID.

        Args:
            project_id: The UUID of the project.

        Returns:
            The Project if found, otherwise None.
        """
        return self._projects.get(project_id)

    def list_projects(self) -> list[Project]:
        """Return all stored projects.

        Returns:
            List of all Project instances.
        """
        return list(self._projects.values())

    def delete_project(self, project_id: str) -> bool:
        """Remove a project by its unique ID.

        Args:
            project_id: The UUID of the project to delete.

        Returns:
            True if the project was found and removed, False otherwise.
        """
        if project_id in self._projects:
            del self._projects[project_id]
            return True
        return False

    # ------------------------------------------------------------------
    # Cloning
    # ------------------------------------------------------------------

    def clone_project(self, project_id: str, new_name: str) -> Optional[Project]:
        """Clone an existing project to create a new independent copy.

        All tasks from the source project are carried over to the clone.
        The clone receives a new unique ID and the provided name.

        Args:
            project_id: The UUID of the project to clone.
            new_name: The name for the cloned project.

        Returns:
            The cloned Project, or None if the source project was not found.
        """
        source = self._projects.get(project_id)
        if source is None:
            return None
        cloned = source.clone(new_name)
        self._projects[cloned.id] = cloned
        return cloned

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def add_task_to_project(
        self,
        project_id: str,
        title: str,
        description: str = "",
        assignee: Optional[str] = None,
        labels: Optional[list[str]] = None,
    ) -> Optional[Task]:
        """Create and add a new task to the specified project.

        Args:
            project_id: The UUID of the target project.
            title: Short summary of the task.
            description: Detailed task description.
            assignee: Optional person responsible.
            labels: Optional categorization tags.

        Returns:
            The newly created Task, or None if the project was not found.
        """
        project = self._projects.get(project_id)
        if project is None:
            return None
        task = Task(
            title=title,
            description=description,
            assignee=assignee,
            labels=labels or [],
        )
        return project.add_task(task)

    def update_task(
        self,
        project_id: str,
        task_id: str,
        **kwargs,
    ) -> Optional[Task]:
        """Update one or more fields on an existing task.

        Supports partial updates — only the fields included as keyword
        arguments will be modified.

        Args:
            project_id: The UUID of the project containing the task.
            task_id: The UUID of the task to update.
            **kwargs: Fields to update. Valid keys are ``title``,
                ``description``, ``status``, ``assignee``, and ``labels``.

        Returns:
            The updated Task, or None if the project or task was not found.
        """
        project = self._projects.get(project_id)
        if project is None:
            return None
        task = project.find_task(task_id)
        if task is None:
            return None

        allowed_fields = {"title", "description", "status", "assignee", "labels"}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(task, key, value)
        return task
