import json

from django.urls import reverse
from rest_framework import status

from tasks.models import Task
from tasks.serializers import TaskWriteSerializer
from users.tests import UserTestMixin


class TestTaskAPIView(UserTestMixin):
    """ Test module for task API """

    PATH = reverse('tasks:task-list')
    TITLE = 'title'
    DESCRIPTION = 'description'

    def setUp(self) -> None:
        super().setUp()
        self._create_superuser()
        self.client.force_login(self.super_user)
        self.test_phrase = 'test_one'
        self.valid_data = {
            self.TITLE: self.test_phrase,
            self.DESCRIPTION: self.test_phrase,
            'assigned_to_id': self.super_user.id
        }

        self.test_task = Task.objects.create(
            **self.valid_data,
            created_by_id=self.super_user.id,
        )

    def test_error_required_fields(self):
        response = self._get_post_response({})
        for key in (self.TITLE, self.DESCRIPTION, 'assigned_to'):
            self.assertEqual(
                response.data[key][0], 'This field is required.'
            )
        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_error_already_exists(self):
        response = self._get_post_response(self.valid_data)

        self.assertEqual(
            response.data[self.TITLE][0],
            'Task with this task name already exists.'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_task(self):
        response = self.client.get(self.PATH)

        self.assertEqual(response.data[0]['id'], self.test_task.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_task(self):
        new_title = 'new_test_title'
        new_description = 'new_test_description'
        data = {
            self.TITLE: new_title,
            self.DESCRIPTION: new_description,
            'assigned_to': self.super_user.id
        }
        response = self._get_post_response(data)

        new_task = Task.objects.get(title=new_title)
        serializer = TaskWriteSerializer(new_task)
        for key, value in serializer.data.items():
            self.assertEqual(
                response.data[key], serializer.data[key]
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_not_allowed(self):
        response = self.client.patch(
            self.PATH, json.dumps({}), content_type='application/json'
        )
        self.assertEqual(
            response.data['detail'], 'Method "PATCH" not allowed.'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

        response = self.client.put(
            self.PATH, json.dumps({}), content_type='application/json'
        )
        self.assertEqual(
            response.data['detail'], 'Method "PUT" not allowed.'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
