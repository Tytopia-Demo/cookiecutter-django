import logging

from celery import shared_task

from .models import User

logger = logging.getLogger(__name__)


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    count = User.objects.count()
    logger.info(
        "Retrieved users count",
        extra={
            "task": "get_users_count",
            "count": count,
        }
    )
    return count
