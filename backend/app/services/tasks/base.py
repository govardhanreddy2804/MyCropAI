from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class TaskResult:
    success: bool
    message: str
    data: Any | None = None


class BackgroundTask(ABC):
    """Base contract for MyCropAI background tasks."""

    @abstractmethod
    def run(self) -> TaskResult:
        """Execute the task and return a standardized result."""
        raise NotImplementedError
