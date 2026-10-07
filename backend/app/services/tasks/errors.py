import logging

logger = logging.getLogger(__name__)


def run_task_safely(task, *args, **kwargs):
    try:
        return task(*args, **kwargs)
    except Exception:
        logger.exception(
            "Background task failed: %s",
            task.__name__,
        )
        return None
