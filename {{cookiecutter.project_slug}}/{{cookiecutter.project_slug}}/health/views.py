"""
Health check views for service monitoring and orchestration.

These endpoints provide standardized health and readiness checks for monitoring
systems, load balancers, and container orchestrators like Kubernetes.
"""
import logging
from datetime import datetime
from typing import Any

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views import View
{%- if cookiecutter.use_celery == 'y' %}
from celery import Celery
{%- endif %}
{%- if cookiecutter.use_drf == 'y' %}
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
{%- endif %}

logger = logging.getLogger(__name__)


def check_database() -> dict[str, Any]:
    """
    Check database connectivity.

    Returns:
        dict: Status information including 'healthy' boolean and optional 'error' message.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return {"healthy": True, "status": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"healthy": False, "status": "disconnected", "error": str(e)}

{%- if cookiecutter.use_celery == 'y' %}


def check_celery() -> dict[str, Any]:
    """
    Check Celery broker connectivity.

    Returns:
        dict: Status information including 'healthy' boolean and optional 'error' message.
    """
    try:
        from celery.app.control import Inspect

        app = Celery()
        inspect = Inspect(app=app)
        stats = inspect.stats(timeout=5.0)
        if stats is None:
            return {"healthy": False, "status": "no_workers", "error": "No Celery workers available"}
        return {"healthy": True, "status": "connected", "workers": len(stats)}
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        return {"healthy": False, "status": "error", "error": str(e)}
{%- endif %}


def perform_health_checks() -> dict[str, Any]:
    """
    Perform all health checks and aggregate results.

    Returns:
        dict: Combined health status with individual check results.
    """
    checks = {
        "database": check_database(),
{%- if cookiecutter.use_celery == 'y' %}
        "celery": check_celery(),
{%- endif %}
    }

    # Overall health is healthy only if all checks pass
    overall_healthy = all(check.get("healthy", False) for check in checks.values())

    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": checks,
    }

{%- if cookiecutter.use_drf == 'y' %}


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request: Request) -> Response:
    """
    Health check endpoint for monitoring systems.

    Returns 200 OK when the service is running and core dependencies are available.
    Returns 503 Service Unavailable if any critical dependency is unhealthy.

    This endpoint is excluded from authentication to allow unrestricted monitoring access.
    """
    health_data = perform_health_checks()
    status_code = 200 if health_data["status"] == "healthy" else 503
    return Response(health_data, status=status_code)


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request: Request) -> Response:
    """
    Readiness check endpoint for load balancers and orchestrators.

    Returns 200 OK only when the service is fully initialized and ready to handle requests.
    Returns 503 Service Unavailable if the service is not ready to accept traffic.

    This endpoint is excluded from authentication to allow unrestricted monitoring access.
    """
    health_data = perform_health_checks()

    # For readiness, we might add additional checks (migrations, cache, etc.)
    # For now, use the same checks as health
    ready = health_data["status"] == "healthy"

    readiness_data = {
        "status": "ready" if ready else "not_ready",
        "timestamp": health_data["timestamp"],
        "checks": health_data["checks"],
    }

    status_code = 200 if ready else 503
    return Response(readiness_data, status=status_code)
{%- else %}


class HealthCheckView(View):
    """
    Health check endpoint for monitoring systems.

    Returns 200 OK when the service is running and core dependencies are available.
    Returns 503 Service Unavailable if any critical dependency is unhealthy.

    This endpoint is excluded from authentication to allow unrestricted monitoring access.
    """

    def get(self, request, *args, **kwargs):
        health_data = perform_health_checks()
        status_code = 200 if health_data["status"] == "healthy" else 503
        return JsonResponse(health_data, status=status_code)


class ReadinessCheckView(View):
    """
    Readiness check endpoint for load balancers and orchestrators.

    Returns 200 OK only when the service is fully initialized and ready to handle requests.
    Returns 503 Service Unavailable if the service is not ready to accept traffic.

    This endpoint is excluded from authentication to allow unrestricted monitoring access.
    """

    def get(self, request, *args, **kwargs):
        health_data = perform_health_checks()

        # For readiness, we might add additional checks (migrations, cache, etc.)
        # For now, use the same checks as health
        ready = health_data["status"] == "healthy"

        readiness_data = {
            "status": "ready" if ready else "not_ready",
            "timestamp": health_data["timestamp"],
            "checks": health_data["checks"],
        }

        status_code = 200 if ready else 503
        return JsonResponse(readiness_data, status=status_code)
{%- endif %}
