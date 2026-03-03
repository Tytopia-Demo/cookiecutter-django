# Structured Logging with Telemetry Context

This project uses structured JSON logging with telemetry context tracking to provide better observability and debugging capabilities.

## Overview

The logging framework provides:

- **Structured JSON logging** in production for easy log aggregation and analysis
- **Request ID generation and propagation** throughout the application lifecycle
- **Telemetry context tracking** (request ID, user ID, session ID, trace ID)
- **Automatic context enrichment** with metadata (timestamp, service name, environment)
- **Standardized log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Context preservation** across async operations, queues, and event handlers

## Configuration

### Environment-specific Settings

#### Production
- Uses JSON-formatted logs for structured logging
- Log level: INFO (configurable via `DJANGO_LOG_LEVEL` environment variable)
- Includes full telemetry context in every log entry
- Optimized for log aggregation tools (e.g., ELK, Splunk, CloudWatch)

#### Local Development
- Uses human-readable plain text logs
- Log level: DEBUG
- Includes telemetry context in a readable format
- Easier to read during development

### Log Format

#### Production (JSON)
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "myapp.views",
  "message": "User login successful",
  "module": "views",
  "function": "login_view",
  "line": 42,
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "12345",
  "session_id": "xyz789",
  "trace_id": "trace-abc-123",
  "service": "{{cookiecutter.project_slug}}",
  "environment": "production"
}
```

#### Local Development (Plain Text)
```
INFO 2024-01-15 10:30:45,123 views 12345 67890 User login successful [request_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890 user_id=12345]
```

## Usage

### Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

def my_view(request):
    logger.info("Processing request")
    logger.debug("Debug information")
    logger.warning("Warning message")
    logger.error("Error occurred")

    try:
        # some operation
        pass
    except Exception as e:
        logger.exception("Exception with stack trace")
```

### Request Context

The `RequestIDMiddleware` automatically:
- Generates a unique request ID for each request
- Captures user ID if authenticated
- Captures session ID if available
- Generates a trace ID for distributed tracing
- Adds these IDs to response headers for client-side correlation

### Celery Tasks

For Celery tasks, use the `task_with_context` decorator to preserve telemetry context:

```python
from celery import shared_task
from {{cookiecutter.project_slug}}.utils.celery import task_with_context, apply_telemetry_context
import logging

logger = logging.getLogger(__name__)

@shared_task
def my_task(param1, param2, _telemetry_context=None):
    # Apply the telemetry context to preserve correlation
    if _telemetry_context:
        apply_telemetry_context(_telemetry_context)

    logger.info(f"Processing task with {param1} and {param2}")
    # Task logic here
```

Or use the decorator:

```python
from celery import shared_task
from {{cookiecutter.project_slug}}.utils.celery import task_with_context

@shared_task
@task_with_context
def my_task(param1, param2):
    logger.info(f"Processing task with {param1} and {param2}")
    # Task logic here
```

## Telemetry Fields

| Field | Description | Source |
|-------|-------------|--------|
| `request_id` | Unique identifier for each HTTP request | Auto-generated or from `X-Request-ID` header |
| `user_id` | ID of authenticated user | Django user session |
| `session_id` | Session identifier | Django session |
| `trace_id` | Distributed tracing ID | Auto-generated or from `X-Trace-ID` header |
| `service` | Service name | Project slug |
| `environment` | Environment name | Settings configuration |

## Request Headers

### Incoming Headers
- `X-Request-ID`: If present, used as the request ID (useful for load balancers)
- `X-Correlation-ID`: Alternative to X-Request-ID
- `X-Trace-ID`: If present, used as the trace ID

### Outgoing Headers
- `X-Request-ID`: Request ID for client-side correlation
- `X-Trace-ID`: Trace ID for distributed tracing

## Log Aggregation

The JSON format is optimized for log aggregation tools. Example queries:

### Find all logs for a specific request
```
request_id:"a1b2c3d4-e5f6-7890-abcd-ef1234567890"
```

### Find all errors for a specific user
```
user_id:"12345" AND level:"ERROR"
```

### Find all logs in a trace
```
trace_id:"trace-abc-123"
```

## Environment Variables

- `DJANGO_LOG_LEVEL`: Set the log level (default: INFO for production, DEBUG for local)
- `DJANGO_READ_DOT_ENV_FILE`: Enable reading from .env file

## Best Practices

1. **Use appropriate log levels**:
   - `DEBUG`: Detailed information for debugging
   - `INFO`: General informational messages
   - `WARNING`: Warning messages for potentially harmful situations
   - `ERROR`: Error messages for error events
   - `CRITICAL`: Critical messages for serious errors

2. **Include context in log messages**:
   ```python
   logger.info("User login", extra={"username": username, "ip": request.META["REMOTE_ADDR"]})
   ```

3. **Use structured logging**:
   ```python
   logger.info("Order processed", extra={"order_id": order.id, "amount": order.total})
   ```

4. **Don't log sensitive information**:
   - Avoid logging passwords, tokens, or other secrets
   - Be careful with PII (Personally Identifiable Information)

5. **Use logger.exception() for errors with stack traces**:
   ```python
   try:
       # code that might raise an exception
   except Exception:
       logger.exception("An error occurred")  # Includes stack trace
   ```

## Customization

To customize the logging configuration, modify `{{cookiecutter.project_slug}}/utils/logging.py`:

- Add custom formatters
- Add custom filters
- Configure additional handlers (e.g., file handlers, external services)
- Modify the log format

## Troubleshooting

### Logs missing telemetry context

Ensure the `RequestIDMiddleware` is properly configured in `MIDDLEWARE` settings.

### Celery tasks not showing context

Use the `task_with_context` decorator or manually apply context using `apply_telemetry_context()`.

### JSON logs in local development

Set `use_json=True` in `local.py` settings if you want JSON logs during development.
