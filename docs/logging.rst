Logging
=======

This project uses structured JSON logging to improve log parsing, searching, and analysis capabilities. Structured logging provides better integration with log aggregation tools and ensures consistent observability across services.

.. _logging-overview:

Overview
--------

The project is configured with:

- **Structured JSON logging** in production and staging environments using ``python-json-logger``
- **Human-readable logging** in development for easier debugging
- **Automatic request context** including request IDs and user IDs
- **Consistent log levels** across all environments (DEBUG, INFO, WARNING, ERROR, CRITICAL)

.. _logging-configuration:

Configuration
-------------

Logging is configured differently based on the environment:

Production/Staging
~~~~~~~~~~~~~~~~~~

In production and staging, logs are output in JSON format with the following fields:

- ``timestamp``: ISO 8601 timestamp
- ``level``: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- ``logger``: Logger name (module path)
- ``message``: Log message
- ``service``: Service name (project slug)
- ``environment``: Environment name (production, staging, etc.)
- ``hostname``: Server hostname
- ``version``: Application version
- ``request_id``: Unique identifier for each request
- ``user_id``: User ID (if authenticated) or "anonymous"
- ``file``: Source file path
- ``line``: Line number in source file
- ``function``: Function name

Example JSON log output:

.. code-block:: json

    {
        "timestamp": "2024-01-15T10:30:45.123Z",
        "level": "INFO",
        "logger": "myapp.views",
        "message": "User logged in successfully",
        "service": "my_project",
        "environment": "production",
        "hostname": "web-server-01",
        "version": "1.0.0",
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "user_id": "12345",
        "file": "/app/myapp/views.py",
        "line": 42,
        "function": "login_view"
    }

Development
~~~~~~~~~~~

In development (``local.py`` settings), logs use a human-readable format for easier debugging:

.. code-block:: text

    INFO 2024-01-15 10:30:45,123 myapp.views User logged in successfully [/app/myapp/views.py:42]

.. _logging-usage:

Usage Examples
--------------

Basic Logging
~~~~~~~~~~~~~

.. code-block:: python

    import logging

    logger = logging.getLogger(__name__)

    # Different log levels
    logger.debug("Detailed debugging information")
    logger.info("General informational message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error message")

Logging with Extra Context
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add additional contextual data to logs:

.. code-block:: python

    import logging

    logger = logging.getLogger(__name__)

    logger.info(
        "User action completed",
        extra={
            "action": "update_profile",
            "user_id": user.id,
            "changes": {"email": "new@example.com"},
        }
    )

This will include the extra fields in the JSON output:

.. code-block:: json

    {
        "timestamp": "2024-01-15T10:30:45.123Z",
        "level": "INFO",
        "message": "User action completed",
        "action": "update_profile",
        "user_id": 12345,
        "changes": {"email": "new@example.com"}
    }

Logging Exceptions
~~~~~~~~~~~~~~~~~~

Always log exceptions with stack traces:

.. code-block:: python

    import logging

    logger = logging.getLogger(__name__)

    try:
        # Some operation that might fail
        result = risky_operation()
    except Exception as e:
        logger.exception("Operation failed", extra={"operation": "risky_operation"})
        # or
        logger.error("Operation failed", exc_info=True, extra={"operation": "risky_operation"})

.. _logging-request-context:

Request Context
---------------

The ``LoggingContextMiddleware`` automatically adds request context to all logs:

- **request_id**: A unique UUID for each request, also included in the ``X-Request-ID`` response header
- **user_id**: The authenticated user's ID, or "anonymous" for unauthenticated requests

This allows you to:

1. Trace a single request through all log entries
2. Correlate logs across microservices using the request ID
3. Filter logs by user for debugging user-specific issues

You can access the request ID in views:

.. code-block:: python

    def my_view(request):
        request_id = request.request_id
        logger.info("Processing request", extra={"request_id": request_id})

.. _logging-best-practices:

Best Practices
--------------

1. **Use appropriate log levels**:

   - ``DEBUG``: Detailed information for diagnosing problems
   - ``INFO``: General informational messages about normal operation
   - ``WARNING``: Unexpected events that don't prevent operation
   - ``ERROR``: Errors that prevent a specific operation
   - ``CRITICAL``: Severe errors that may prevent the entire application from running

2. **Include context**: Add relevant contextual information using the ``extra`` parameter

3. **Don't log sensitive data**: Never log passwords, tokens, credit card numbers, or other sensitive information

4. **Use structured data**: When adding extra fields, use dictionaries and simple types that serialize to JSON

5. **Be consistent**: Use consistent field names across the application:

   - Use ``user_id`` not ``userId`` or ``user``
   - Use ``request_id`` not ``requestId`` or ``correlation_id``
   - Follow the existing naming conventions

6. **Log at appropriate boundaries**: Log at service boundaries (API calls, database queries, external service calls)

.. _logging-environment-variables:

Environment Variables
---------------------

The following environment variables affect logging:

- ``ENVIRONMENT``: Sets the environment name in logs (default: "development" in base settings, "production" in production)
- ``DJANGO_LOG_SQL``: In development, set to "true" to enable SQL query logging
- ``DJANGO_SENTRY_LOG_LEVEL``: When using Sentry, sets the log level for Sentry integration (default: INFO)

.. _logging-third-party:

Third-Party Integration
-----------------------

The JSON log format integrates seamlessly with log aggregation and analysis tools:

- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Splunk**
- **Datadog**
- **CloudWatch Logs**
- **Google Cloud Logging**
- **Azure Monitor**

These tools can automatically parse the JSON logs and provide:

- Full-text search across all log fields
- Time-series analysis
- Real-time alerting
- Dashboard creation
- Log correlation and tracing

.. _logging-troubleshooting:

Troubleshooting
---------------

Logs not appearing
~~~~~~~~~~~~~~~~~~

1. Check that the ``LOGGING`` configuration is properly loaded
2. Verify the log level is appropriate (e.g., DEBUG logs won't appear if level is set to INFO)
3. Ensure the logger name matches your module name

Logs not in JSON format
~~~~~~~~~~~~~~~~~~~~~~~~

1. Verify you're using the production settings (``production.py``)
2. Check that ``python-json-logger`` is installed: ``pip list | grep python-json-logger``
3. Verify the formatter is set to ``json`` in the handler configuration

Missing request context
~~~~~~~~~~~~~~~~~~~~~~~~

1. Ensure ``LoggingContextMiddleware`` is in the ``MIDDLEWARE`` list
2. Verify it's placed after authentication middleware
3. Check that the middleware is not raising exceptions

.. _logging-migration:

Migration from Plain Text
-------------------------

If you have existing plain text logging:

1. Replace ``logging.basicConfig()`` calls with the Django ``LOGGING`` configuration
2. Update any custom formatters to use the JSON formatter
3. Remove any ``print()`` statements and replace with ``logger`` calls
4. Test in development first before deploying to production

.. seealso::

   - `Django Logging Documentation <https://docs.djangoproject.com/en/stable/topics/logging/>`_
   - `Python Logging Documentation <https://docs.python.org/3/library/logging.html>`_
   - `python-json-logger <https://github.com/madzak/python-json-logger>`_
