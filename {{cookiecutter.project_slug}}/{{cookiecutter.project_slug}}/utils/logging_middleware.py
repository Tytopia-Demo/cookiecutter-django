"""
Middleware for adding contextual information to logs.

This middleware adds request_id and user_id to the logging context,
making it easier to trace requests through the system and correlate
logs across different services.
"""

import logging
import uuid
from typing import Callable

from django.http import HttpRequest
from django.http import HttpResponse

logger = logging.getLogger(__name__)


class LoggingContextMiddleware:
    """
    Middleware that adds contextual information to logs.

    Adds the following fields to the logging context:
    - request_id: A unique identifier for each request
    - user_id: The ID of the authenticated user (if available)

    These fields are automatically included in all log records
    when using the structured JSON logger.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())

        # Get user ID if user is authenticated
        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = str(request.user.pk)

        # Create a custom log adapter that adds context
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = request_id
            record.user_id = user_id or "anonymous"
            return record

        logging.setLogRecordFactory(record_factory)

        try:
            # Store request_id on the request object for later use
            request.request_id = request_id

            # Add request_id to response headers for tracing
            response = self.get_response(request)
            response["X-Request-ID"] = request_id

            return response
        finally:
            # Restore the original factory
            logging.setLogRecordFactory(old_factory)
