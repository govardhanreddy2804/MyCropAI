from collections.abc import Callable
from typing import Any

from fastapi import BackgroundTasks

from app.services.tasks.errors import run_task_safely


class TaskRunner:
    """Application-level abstraction over FastAPI background tasks."""

    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def add_task(
        self,
        task: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.background_tasks.add_task(
            run_task_safely,
            task,
            *args,
            **kwargs,
        )
