"""Data models for ProjectFlow.

Defines the core domain objects — Task and Project — used throughout the
application. Both are implemented as dataclasses for clarity and ease of
serialization.
"""

import uuid
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass
class Task:
    """Represents a single actionable item within a project.

    Attributes:
        id: Unique identifier (auto-generated UUID).
        title: Short summary of what needs to be done.
        description: Detailed explanation of the task requirements.
        status: Current state — one of ``todo``, ``in_progress``, or ``done``.
        assignee: Optional name or email of the person responsible.
        labels: Categorization tags for filtering and organization.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: str = "todo"
    assignee: Optional[str] = None
    labels: list = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialize the task to a plain dictionary."""
        return asdict(self)


@dataclass
class Project:
    """Represents a project containing an ordered collection of tasks.

    Attributes:
        id: Unique identifier (auto-generated UUID).
        name: Human-readable project name.
        description: Overview of the project's purpose and scope.
        tasks: Ordered list of tasks belonging to this project.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    tasks: list = field(default_factory=list)

    def clone(self, new_name: str) -> "Project":
        """Create an independent copy of this project for use as a template.

        Produces a new project with a unique ID and the specified name,
        carrying over the description and all existing tasks. The cloned
        project is fully independent of the original — modifications to
        one should never affect the other.

        Args:
            new_name: The name for the newly created project.

        Returns:
            A new Project instance with its own copies of all tasks.
        """
        cloned_tasks = list(self.tasks)
        return Project(
            id=str(uuid.uuid4()),
            name=new_name,
            description=self.description,
            tasks=cloned_tasks,
        )

    def add_task(self, task: Task) -> Task:
        """Append a task to this project's task list.

        Args:
            task: The Task instance to add.

        Returns:
            The task that was added.
        """
        self.tasks.append(task)
        return task

    def find_task(self, task_id: str) -> Optional[Task]:
        """Look up a task by its unique identifier.

        Args:
            task_id: The UUID of the task to find.

        Returns:
            The matching Task, or None if no task has that ID.
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def to_dict(self) -> dict:
        """Serialize the project and all its tasks to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
        }
