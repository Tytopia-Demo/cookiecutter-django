"""Custom logging configuration with telemetry context."""
import logging

from pythonjsonlogger import jsonlogger

from .middleware import get_request_id
from .middleware import get_session_id
from .middleware import get_trace_id
from .middleware import get_user_id


class TelemetryContextFilter(logging.Filter):
    """
    Logging filter that adds telemetry context to log records.

    Adds request ID, user ID, session ID, and trace ID to all log records
    for correlation and debugging purposes.
    """

    def filter(self, record):
        """Add telemetry context to the log record."""
        record.request_id = get_request_id() or "-"
        record.user_id = get_user_id() or "-"
        record.session_id = get_session_id() or "-"
        record.trace_id = get_trace_id() or "-"
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that includes telemetry context and metadata.

    Formats log records as JSON with standardized fields including:
    - timestamp: ISO 8601 formatted timestamp
    - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - message: Log message
    - logger: Logger name
    - module: Module name
    - function: Function name
    - line: Line number
    - request_id: Request ID for correlation
    - user_id: User ID if authenticated
    - session_id: Session ID if available
    - trace_id: Trace ID for distributed tracing
    - service: Service name
    - environment: Environment name
    """

    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to the JSON log record."""
        super().add_fields(log_record, record, message_dict)

        # Standardize field names
        if "asctime" in log_record:
            log_record["timestamp"] = log_record.pop("asctime")
        if "levelname" in log_record:
            log_record["level"] = log_record.pop("levelname")
        if "name" in log_record:
            log_record["logger"] = log_record.pop("name")

        # Add telemetry context (will be set by TelemetryContextFilter)
        log_record["request_id"] = getattr(record, "request_id", "-")
        log_record["user_id"] = getattr(record, "user_id", "-")
        log_record["session_id"] = getattr(record, "session_id", "-")
        log_record["trace_id"] = getattr(record, "trace_id", "-")

        # Add metadata (these will be set from settings)
        log_record["service"] = getattr(record, "service", "{{cookiecutter.project_slug}}")
        log_record["environment"] = getattr(record, "environment", "unknown")


def get_logging_config(environment="production", log_level="INFO", use_json=True):
    """
    Get logging configuration dictionary.

    Args:
        environment: Environment name (local, staging, production)
        log_level: Default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting (True for production)

    Returns:
        Dictionary with logging configuration
    """
    # Base formatters
    formatters = {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s [request_id=%(request_id)s user_id=%(user_id)s]",
        },
    }

    if use_json:
        formatters["json"] = {
            "()": "{{cookiecutter.project_slug}}.utils.logging.CustomJsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
        default_formatter = "json"
    else:
        default_formatter = "verbose"

    # Base filters
    filters = {
        "telemetry_context": {
            "()": "{{cookiecutter.project_slug}}.utils.logging.TelemetryContextFilter",
        },
    }

    # Base handlers
    handlers = {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": default_formatter,
            "filters": ["telemetry_context"],
        },
    }

    # Base loggers
    loggers = {
        "django.db.backends": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False,
        },
    }

    # Environment-specific configuration
    if environment == "production":
        # In production, we want structured logging
        handlers["console"]["level"] = "INFO"
        loggers.update({
            "sentry_sdk": {
                "level": "ERROR",
                "handlers": ["console"],
                "propagate": False,
            },
        })
    elif environment == "local":
        # In local development, more verbose output
        handlers["console"]["level"] = "DEBUG"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "filters": filters,
        "handlers": handlers,
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
        "loggers": loggers,
    }
