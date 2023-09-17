from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tasks.views import TaskViewSet

app_name = 'tasks'

router = DefaultRouter()
router.register(r'', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
