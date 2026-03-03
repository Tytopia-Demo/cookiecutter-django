"""Celery utilities for context preservation and telemetry."""
import functools
import logging

from .middleware import get_request_id
from .middleware import get_session_id
from .middleware import get_trace_id
from .middleware import get_user_id

logger = logging.getLogger(__name__)


def task_with_context(func):
    """
    Decorator to preserve telemetry context in Celery tasks.

    This decorator captures the current request context (request ID, user ID,
    session ID, trace ID) when the task is called and propagates it to the
    task execution so that logs generated within the task include proper
    correlation identifiers.

    Usage:
        from {{ cookiecutter.project_slug }}.utils.celery import task_with_context

        @app.task
        @task_with_context
        def my_task(param1, param2):
            logger.info("This log will include request_id, user_id, etc.")
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Capture context at the time of task invocation
        context = {
            "request_id": get_request_id(),
            "user_id": get_user_id(),
            "session_id": get_session_id(),
            "trace_id": get_trace_id(),
        }

        # Pass context to the task as additional kwargs
        kwargs["_telemetry_context"] = context
        return func(*args, **kwargs)

    return wrapper


def apply_telemetry_context(context):
    """
    Apply telemetry context to the current thread.

    This is typically called at the beginning of a Celery task to restore
    the context that was captured when the task was invoked.

    Args:
        context: Dictionary with telemetry context fields

    Usage:
        @app.task
        def my_task(param1, param2, _telemetry_context=None):
            if _telemetry_context:
                apply_telemetry_context(_telemetry_context)

            logger.info("This log will include the propagated context")
            ...
    """
    from .middleware import _thread_locals

    if context:
        for key, value in context.items():
            if value:
                setattr(_thread_locals, key, value)
