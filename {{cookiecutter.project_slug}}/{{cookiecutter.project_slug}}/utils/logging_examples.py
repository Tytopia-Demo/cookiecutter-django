"""
Logging usage examples and utilities.

This module demonstrates best practices for structured logging
in the application. Use these patterns throughout your code.
"""

import logging
from functools import wraps
from typing import Any
from typing import Callable

logger = logging.getLogger(__name__)


def log_function_call(func: Callable) -> Callable:
    """
    Decorator that logs function calls with arguments and execution time.

    Example:
        @log_function_call
        def process_payment(user_id, amount):
            # Process payment logic
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(
            f"Calling {func.__name__}",
            extra={
                "function": func.__name__,
                "args": str(args)[:100],  # Truncate to avoid logging large data
                "kwargs": str(kwargs)[:100],
            }
        )
        try:
            result = func(*args, **kwargs)
            logger.info(
                f"Completed {func.__name__}",
                extra={"function": func.__name__}
            )
            return result
        except Exception as e:
            logger.exception(
                f"Error in {func.__name__}",
                extra={
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                }
            )
            raise

    return wrapper


class LoggerMixin:
    """
    Mixin class that provides a logger instance configured for the class.

    Usage:
        class MyView(LoggerMixin, View):
            def get(self, request):
                self.logger.info("Processing GET request")
                return Response()
    """

    @property
    def logger(self) -> logging.Logger:
        """Return a logger instance for this class."""
        if not hasattr(self, "_logger"):
            self._logger = logging.getLogger(
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger


def log_api_call(service: str, endpoint: str, **extra_context: Any) -> None:
    """
    Log an external API call with consistent structure.

    Args:
        service: Name of the external service (e.g., "stripe", "sendgrid")
        endpoint: API endpoint being called
        **extra_context: Additional context to include in the log

    Example:
        log_api_call(
            "stripe",
            "/v1/charges",
            method="POST",
            amount=1000,
            currency="usd"
        )
    """
    logger.info(
        f"API call to {service}",
        extra={
            "api_service": service,
            "api_endpoint": endpoint,
            **extra_context,
        }
    )


def log_database_query(operation: str, table: str, **extra_context: Any) -> None:
    """
    Log database operations with consistent structure.

    Args:
        operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
        table: Database table name
        **extra_context: Additional context to include in the log

    Example:
        log_database_query(
            "UPDATE",
            "users",
            user_id=123,
            fields_updated=["email", "last_login"]
        )
    """
    logger.debug(
        f"Database {operation} on {table}",
        extra={
            "db_operation": operation,
            "db_table": table,
            **extra_context,
        }
    )


def log_user_action(action: str, user_id: int, **extra_context: Any) -> None:
    """
    Log user actions with consistent structure.

    Args:
        action: Description of the action
        user_id: ID of the user performing the action
        **extra_context: Additional context to include in the log

    Example:
        log_user_action(
            "profile_updated",
            user_id=123,
            changes={"email": "new@example.com"}
        )
    """
    logger.info(
        f"User action: {action}",
        extra={
            "user_action": action,
            "user_id": user_id,
            **extra_context,
        }
    )


def log_security_event(event_type: str, severity: str = "warning", **extra_context: Any) -> None:
    """
    Log security-related events.

    Args:
        event_type: Type of security event (e.g., "failed_login", "permission_denied")
        severity: Severity level ("info", "warning", "error", "critical")
        **extra_context: Additional context to include in the log

    Example:
        log_security_event(
            "failed_login",
            severity="warning",
            username="john@example.com",
            ip_address="192.168.1.1",
            attempts=3
        )
    """
    log_func = getattr(logger, severity, logger.warning)
    log_func(
        f"Security event: {event_type}",
        extra={
            "security_event": event_type,
            "severity": severity,
            **extra_context,
        }
    )


# Example usage in views
def example_view_logging(request):
    """Example of logging in a Django view."""
    # Log the incoming request
    logger.info(
        "Processing user request",
        extra={
            "path": request.path,
            "method": request.method,
            "user_id": request.user.id if request.user.is_authenticated else None,
        }
    )

    try:
        # Your business logic here
        result = perform_operation()

        # Log successful completion
        logger.info(
            "Request processed successfully",
            extra={
                "path": request.path,
                "result": str(result)[:100],  # Truncate to avoid logging large data
            }
        )

        return result

    except ValueError as e:
        # Log validation errors at warning level
        logger.warning(
            "Validation error in request",
            extra={
                "path": request.path,
                "error": str(e),
            }
        )
        raise

    except Exception as e:
        # Log unexpected errors at error level with full stack trace
        logger.exception(
            "Unexpected error processing request",
            extra={
                "path": request.path,
                "error_type": type(e).__name__,
            }
        )
        raise


def perform_operation():
    """Placeholder for business logic."""
    pass
