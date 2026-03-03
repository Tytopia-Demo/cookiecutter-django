"""Middleware for request ID generation and telemetry context."""
import uuid
from threading import local

from django.utils.deprecation import MiddlewareMixin

# Thread-local storage for request context
_thread_locals = local()


def get_request_id():
    """Get the current request ID from thread-local storage."""
    return getattr(_thread_locals, "request_id", None)


def get_user_id():
    """Get the current user ID from thread-local storage."""
    return getattr(_thread_locals, "user_id", None)


def get_session_id():
    """Get the current session ID from thread-local storage."""
    return getattr(_thread_locals, "session_id", None)


def get_trace_id():
    """Get the current trace ID from thread-local storage."""
    return getattr(_thread_locals, "trace_id", None)


class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware to generate and propagate request IDs throughout the application.

    This middleware:
    - Generates a unique request ID for each incoming request
    - Stores the request ID in thread-local storage for access in logging
    - Adds the request ID to the response headers for client-side correlation
    - Captures user, session, and trace information for telemetry
    """

    def process_request(self, request):
        """
        Process incoming request to generate and store request context.

        Checks for existing request ID in headers (e.g., from load balancers)
        or generates a new one. Also captures user and session information.
        """
        # Get or generate request ID
        request_id = request.META.get(
            "HTTP_X_REQUEST_ID",
            request.META.get("HTTP_X_CORRELATION_ID", str(uuid.uuid4())),
        )
        request.request_id = request_id
        _thread_locals.request_id = request_id

        # Get or generate trace ID (for distributed tracing)
        trace_id = request.META.get("HTTP_X_TRACE_ID", str(uuid.uuid4()))
        request.trace_id = trace_id
        _thread_locals.trace_id = trace_id

        # Store user information if authenticated
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = str(request.user.pk)
            request.user_id = user_id
            _thread_locals.user_id = user_id
        else:
            _thread_locals.user_id = None

        # Store session ID if available
        if hasattr(request, "session") and request.session.session_key:
            session_id = request.session.session_key
            request.session_id = session_id
            _thread_locals.session_id = session_id
        else:
            _thread_locals.session_id = None

    def process_response(self, request, response):
        """
        Process outgoing response to add request ID to headers.

        This allows clients to correlate logs with specific requests.
        """
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        if hasattr(request, "trace_id"):
            response["X-Trace-ID"] = request.trace_id

        # Clean up thread-local storage
        self._cleanup_thread_locals()

        return response

    def process_exception(self, request, exception):
        """Clean up thread-local storage on exception."""
        self._cleanup_thread_locals()
        return None

    @staticmethod
    def _cleanup_thread_locals():
        """Remove request context from thread-local storage."""
        for attr in ["request_id", "user_id", "session_id", "trace_id"]:
            if hasattr(_thread_locals, attr):
                delattr(_thread_locals, attr)
