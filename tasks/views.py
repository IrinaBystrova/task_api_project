from rest_framework import permissions, viewsets

from tasks.models import Task
from tasks.permissions import IsAuthorOrReadOnly
from tasks.serializers import TaskReadSerializer, TaskWriteSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD tasks
    """

    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return TaskWriteSerializer

        return TaskReadSerializer

    def get_permissions(self):
        if self.action in ('create',):
            self.permission_classes = (permissions.IsAuthenticated,)
        elif self.action in ('update', 'partial_update', 'destroy'):
            self.permission_classes = (IsAuthorOrReadOnly,)
        else:
            self.permission_classes = (permissions.AllowAny,)

        return super().get_permissions()
