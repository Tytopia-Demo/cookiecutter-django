from django.urls import path
{%- if cookiecutter.use_drf == 'y' %}

from .views import health_check
from .views import readiness_check
{%- else %}

from .views import HealthCheckView
from .views import ReadinessCheckView
{%- endif %}

app_name = "health"

{%- if cookiecutter.use_drf == 'y' %}
urlpatterns = [
    path("", health_check, name="health"),
    path("ready/", readiness_check, name="ready"),
]
{%- else %}
urlpatterns = [
    path("", HealthCheckView.as_view(), name="health"),
    path("ready/", ReadinessCheckView.as_view(), name="ready"),
]
{%- endif %}
