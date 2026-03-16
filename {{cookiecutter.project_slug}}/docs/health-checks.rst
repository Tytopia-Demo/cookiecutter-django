Health Check Endpoints
======================

This project includes standardized health and readiness endpoints for monitoring, orchestration, and operational visibility.

Overview
--------

Health endpoints indicate whether a service is functioning correctly, while readiness endpoints signal when a service is prepared to accept traffic. These endpoints are essential for:

* Load balancers
* Container orchestrators (like Kubernetes)
* Monitoring systems
* Auto-scaling decisions
* Traffic routing

Endpoints
---------

Health Check Endpoint
~~~~~~~~~~~~~~~~~~~~~

**URL:** ``/health/``

**Method:** GET

**Authentication:** None required (publicly accessible)

**Description:** Returns the current health status of the service and its critical dependencies.

**Response Format:**

.. code-block:: json

    {
        "status": "healthy",
        "timestamp": "2024-01-15T12:34:56.789Z",
        "checks": {
            "database": {
                "healthy": true,
                "status": "connected"
            }{% if cookiecutter.use_celery == 'y' %},
            "celery": {
                "healthy": true,
                "status": "connected",
                "workers": 2
            }{% endif %}
        }
    }

**Status Codes:**

* ``200 OK`` - Service is healthy and all dependencies are available
* ``503 Service Unavailable`` - Service or one or more critical dependencies are unhealthy

Readiness Check Endpoint
~~~~~~~~~~~~~~~~~~~~~~~~

**URL:** ``/health/ready/``

**Method:** GET

**Authentication:** None required (publicly accessible)

**Description:** Returns whether the service is fully initialized and ready to handle requests.

**Response Format:**

.. code-block:: json

    {
        "status": "ready",
        "timestamp": "2024-01-15T12:34:56.789Z",
        "checks": {
            "database": {
                "healthy": true,
                "status": "connected"
            }{% if cookiecutter.use_celery == 'y' %},
            "celery": {
                "healthy": true,
                "status": "connected",
                "workers": 2
            }{% endif %}
        }
    }

**Status Codes:**

* ``200 OK`` - Service is ready to accept traffic
* ``503 Service Unavailable`` - Service is not ready to accept traffic

Health Checks
-------------

The following health checks are performed:

Database Check
~~~~~~~~~~~~~~

Verifies that the database connection is active and can execute queries.

* **Check:** Executes a simple ``SELECT 1`` query
* **Timeout:** Inherits from database connection timeout settings
* **Failure Impact:** Service considered unhealthy/not ready

{% if cookiecutter.use_celery == 'y' -%}
Celery Check
~~~~~~~~~~~~

Verifies that Celery workers are available and the message broker is accessible.

* **Check:** Queries Celery worker statistics via the broker
* **Timeout:** 5 seconds
* **Failure Impact:** Service considered unhealthy/not ready
{%- endif %}

Configuration
-------------

Health Check Timeouts
~~~~~~~~~~~~~~~~~~~~~

Health checks are designed to complete quickly to avoid blocking monitoring systems:

* Database check: Uses Django's configured database timeout (default: 5 seconds)
{% if cookiecutter.use_celery == 'y' -%}
* Celery check: 5 second timeout
{%- endif %}

Logging
~~~~~~~

Health check logging is configured to minimize noise from frequent monitoring requests. Only warnings and errors from the health check module are logged. This is configured in ``config/settings/base.py``:

.. code-block:: python

    LOGGING = {
        ...
        "loggers": {
            "{{ cookiecutter.project_slug }}.health": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }

Usage Examples
--------------

Kubernetes
~~~~~~~~~~

Use health endpoints in Kubernetes liveness and readiness probes:

.. code-block:: yaml

    apiVersion: v1
    kind: Pod
    metadata:
      name: {{ cookiecutter.project_slug }}
    spec:
      containers:
      - name: {{ cookiecutter.project_slug }}
        image: {{ cookiecutter.project_slug }}:latest
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health/ready/
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 5
          failureThreshold: 3

Docker Compose
~~~~~~~~~~~~~~

Add health checks to Docker Compose services:

.. code-block:: yaml

    services:
      django:
        build: .
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
          interval: 30s
          timeout: 10s
          retries: 3
          start_period: 40s

Load Balancers
~~~~~~~~~~~~~~

Configure your load balancer to use the health endpoint for backend health checks. For example, with AWS Application Load Balancer:

* **Health check path:** ``/health/``
* **Success codes:** ``200``
* **Interval:** 30 seconds
* **Timeout:** 5 seconds
* **Healthy threshold:** 2 consecutive successes
* **Unhealthy threshold:** 3 consecutive failures

Monitoring
~~~~~~~~~~

Use the health endpoint with monitoring tools like Prometheus, Datadog, or Nagios:

.. code-block:: bash

    # Simple curl check
    curl -f http://localhost:8000/health/

    # Check with timeout
    curl --max-time 5 -f http://localhost:8000/health/

    # Check exit code for scripting
    if curl -sf http://localhost:8000/health/ > /dev/null; then
        echo "Service is healthy"
    else
        echo "Service is unhealthy"
    fi

Testing
-------

The health check endpoints include comprehensive test coverage. Run tests with:

.. code-block:: bash

    pytest {{ cookiecutter.project_slug }}/health/tests/

Key test scenarios covered:

* Health endpoint returns 200 when all dependencies are healthy
* Readiness endpoint returns 200 when service is ready
* Both endpoints include all configured health checks
* Endpoints are accessible without authentication
* Response format matches specification

Extending Health Checks
------------------------

To add custom health checks, modify ``{{ cookiecutter.project_slug }}/health/views.py``:

.. code-block:: python

    def check_custom_service() -> dict[str, Any]:
        """Check custom service availability."""
        try:
            # Perform your health check
            result = custom_service.ping()
            return {"healthy": True, "status": "connected"}
        except Exception as e:
            logger.error(f"Custom service health check failed: {e}")
            return {"healthy": False, "status": "error", "error": str(e)}

    def perform_health_checks() -> dict[str, Any]:
        """Perform all health checks and aggregate results."""
        checks = {
            "database": check_database(),
            "custom_service": check_custom_service(),  # Add your check here
        }
        # ... rest of the function

Troubleshooting
---------------

Health Check Always Returns Unhealthy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Check the response JSON to see which specific check is failing
2. Review application logs for error messages from health checks
3. Verify that all dependencies (database{% if cookiecutter.use_celery == 'y' %}, Celery workers{% endif %}) are running
4. Ensure network connectivity to all checked services

{% if cookiecutter.use_celery == 'y' -%}
Celery Check Fails
~~~~~~~~~~~~~~~~~~

If the Celery health check consistently fails:

1. Verify Celery workers are running: ``celery -A config.celery_app worker --loglevel=info``
2. Check Celery broker (Redis/RabbitMQ) is accessible
3. Review Celery configuration in settings
4. Check for firewall rules blocking broker connections
{%- endif %}

Health Check Times Out
~~~~~~~~~~~~~~~~~~~~~~

If health checks are timing out:

1. Review database query performance
{% if cookiecutter.use_celery == 'y' -%}
2. Check Celery broker response time
3. Consider adjusting timeout values in health check functions
{%- else -%}
2. Consider adjusting timeout values in health check functions
{%- endif %}
3. Ensure health checks are not performing expensive operations

Best Practices
--------------

1. **Keep Health Checks Fast:** Health checks should complete in under 5 seconds
2. **Check Critical Dependencies Only:** Only check services essential for application operation
3. **Use Appropriate Timeouts:** Set timeouts to prevent blocking monitoring systems
4. **Monitor Health Check Performance:** Track health check response times and failures
5. **Differentiate Health vs Readiness:** Health indicates service is running, readiness indicates service can handle traffic
6. **Don't Require Authentication:** Health endpoints should be publicly accessible for monitoring
7. **Return Structured JSON:** Always return consistent JSON format with status and timestamp
8. **Log Failures Only:** Minimize logging of successful health checks to reduce noise
