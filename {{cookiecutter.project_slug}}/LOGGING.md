# Structured JSON Logging

This project is configured with structured JSON logging to provide better observability and easier integration with log aggregation tools.

## Quick Start

### Production Logging

In production, all logs are output in JSON format with contextual metadata:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "myapp.views",
  "message": "User logged in successfully",
  "service": "{{ cookiecutter.project_slug }}",
  "environment": "production",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "12345"
}
```

### Development Logging

In development (local.py), logs use a human-readable format:

```
INFO 2024-01-15 10:30:45,123 myapp.views User logged in successfully [/app/myapp/views.py:42]
```

## Usage

### Basic Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("User action completed")
logger.warning("Unexpected condition")
logger.error("Operation failed")
```

### Logging with Context

Add extra fields to provide more context:

```python
logger.info(
    "User profile updated",
    extra={
        "user_id": user.id,
        "fields_updated": ["email", "name"],
    }
)
```

### Request Context

The `LoggingContextMiddleware` automatically adds:
- `request_id`: Unique ID for each request (also in X-Request-ID header)
- `user_id`: Authenticated user's ID or "anonymous"

## Configuration

### Environment Variables

Set the `ENVIRONMENT` variable to control the environment field in logs:
- `ENVIRONMENT=production` for production
- `ENVIRONMENT=staging` for staging
- `ENVIRONMENT=development` for development (default)

### Enable SQL Logging

In development, set `DJANGO_LOG_SQL=true` to see all SQL queries in logs.

## Documentation

See the full documentation at `docs/logging.rst` for:
- Complete configuration reference
- Best practices
- Integration with log aggregation tools
- Troubleshooting guide

## Examples

Check `{{ cookiecutter.project_slug }}/utils/logging_examples.py` for:
- Logging decorators
- Logging mixins for classes
- Helper functions for common patterns
- Example usage in views

## Integration

The JSON log format works seamlessly with:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- Datadog
- CloudWatch Logs
- Google Cloud Logging
- Azure Monitor
