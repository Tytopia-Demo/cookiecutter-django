import logging

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from {{ cookiecutter.project_slug }}.users.models import User

from .serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    {%- if cookiecutter.username_type == "email" %}
    lookup_field = "pk"
    {%- else %}
    lookup_field = "username"
    {%- endif %}

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        logger.debug(
            "User accessed their profile via API",
            extra={"user_id": request.user.id, "endpoint": "me"}
        )
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def perform_update(self, serializer):
        """Log API updates with structured context."""
        logger.info(
            "User updated via API",
            extra={
                "user_id": self.request.user.id,
                "updated_fields": list(serializer.validated_data.keys()),
            }
        )
        super().perform_update(serializer)
