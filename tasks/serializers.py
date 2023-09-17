from rest_framework import serializers

from tasks.models import Task


class TaskReadSerializer(serializers.ModelSerializer):
    created_by = serializers.CharField(
        source='created_by.username', read_only=True
    )
    assigned_to = serializers.CharField(
        source='assigned_to.username', read_only=True
    )

    class Meta:
        model = Task
        fields = '__all__'


class TaskWriteSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Task
        fields = '__all__'
