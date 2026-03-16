"""Tests for health check endpoints."""
{%- if cookiecutter.use_drf == 'y' %}
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


class TestHealthCheckEndpoint:
    """Test suite for health check endpoint."""

    def test_health_check_returns_200_when_healthy(self):
        """Test that health check returns 200 when all dependencies are healthy."""
        client = APIClient()
        url = reverse("health:health")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "status" in response.data
        assert response.data["status"] == "healthy"
        assert "timestamp" in response.data
        assert "checks" in response.data

    def test_health_check_includes_database_check(self):
        """Test that health check includes database status."""
        client = APIClient()
        url = reverse("health:health")
        response = client.get(url)

        assert "checks" in response.data
        assert "database" in response.data["checks"]
        assert response.data["checks"]["database"]["healthy"] is True

{%- if cookiecutter.use_celery == 'y' %}

    def test_health_check_includes_celery_check(self):
        """Test that health check includes Celery status."""
        client = APIClient()
        url = reverse("health:health")
        response = client.get(url)

        assert "checks" in response.data
        assert "celery" in response.data["checks"]
{%- endif %}

    def test_health_check_no_authentication_required(self):
        """Test that health check endpoint does not require authentication."""
        client = APIClient()
        # Explicitly don't authenticate
        url = reverse("health:health")
        response = client.get(url)

        # Should not return 401 or 403
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]


class TestReadinessCheckEndpoint:
    """Test suite for readiness check endpoint."""

    def test_readiness_check_returns_200_when_ready(self):
        """Test that readiness check returns 200 when service is ready."""
        client = APIClient()
        url = reverse("health:ready")
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "status" in response.data
        assert response.data["status"] == "ready"
        assert "timestamp" in response.data
        assert "checks" in response.data

    def test_readiness_check_includes_database_check(self):
        """Test that readiness check includes database status."""
        client = APIClient()
        url = reverse("health:ready")
        response = client.get(url)

        assert "checks" in response.data
        assert "database" in response.data["checks"]
        assert response.data["checks"]["database"]["healthy"] is True

    def test_readiness_check_no_authentication_required(self):
        """Test that readiness check endpoint does not require authentication."""
        client = APIClient()
        # Explicitly don't authenticate
        url = reverse("health:ready")
        response = client.get(url)

        # Should not return 401 or 403
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
{%- else %}
import pytest
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


class TestHealthCheckEndpoint:
    """Test suite for health check endpoint."""

    def test_health_check_returns_200_when_healthy(self):
        """Test that health check returns 200 when all dependencies are healthy."""
        client = Client()
        url = reverse("health:health")
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "checks" in data

    def test_health_check_includes_database_check(self):
        """Test that health check includes database status."""
        client = Client()
        url = reverse("health:health")
        response = client.get(url)

        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["healthy"] is True

{%- if cookiecutter.use_celery == 'y' %}

    def test_health_check_includes_celery_check(self):
        """Test that health check includes Celery status."""
        client = Client()
        url = reverse("health:health")
        response = client.get(url)

        data = response.json()
        assert "checks" in data
        assert "celery" in data["checks"]
{%- endif %}

    def test_health_check_no_authentication_required(self):
        """Test that health check endpoint does not require authentication."""
        client = Client()
        # Explicitly don't authenticate
        url = reverse("health:health")
        response = client.get(url)

        # Should not return 401 or 403
        assert response.status_code in [200, 503]


class TestReadinessCheckEndpoint:
    """Test suite for readiness check endpoint."""

    def test_readiness_check_returns_200_when_ready(self):
        """Test that readiness check returns 200 when service is ready."""
        client = Client()
        url = reverse("health:ready")
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ready"
        assert "timestamp" in data
        assert "checks" in data

    def test_readiness_check_includes_database_check(self):
        """Test that readiness check includes database status."""
        client = Client()
        url = reverse("health:ready")
        response = client.get(url)

        data = response.json()
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["healthy"] is True

    def test_readiness_check_no_authentication_required(self):
        """Test that readiness check endpoint does not require authentication."""
        client = Client()
        # Explicitly don't authenticate
        url = reverse("health:ready")
        response = client.get(url)

        # Should not return 401 or 403
        assert response.status_code in [200, 503]
{%- endif %}
