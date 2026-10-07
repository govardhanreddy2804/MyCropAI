from app.services.tasks.base import BackgroundTask, TaskResult


class ExampleTask(BackgroundTask):
    def run(self) -> TaskResult:
        return TaskResult(
            success=True,
            message="Task completed",
        )


def test_background_task_returns_result():
    result = ExampleTask().run()

    assert result.success is True
    assert result.message == "Task completed"
