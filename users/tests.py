import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from users.models import CustomUser
from users.serializers import (
    UserRegisterationSerializer, CustomUserSerializer, UserLoginSerializer,
)


class UserTestMixin(TestCase):
    PATH = ''
    EMAIL = 'email'
    USERNAME = 'username'
    PASSWORD = 'password'
    TOKENS = 'tokens'
    REFRESH = 'refresh'
    ACCESS = 'access'

    def setUp(self) -> None:
        super().setUp()
        self.valid_data = {
            self.EMAIL: 'test@test.com',
            self.USERNAME: 'Guido',
            self.PASSWORD: 'van_Rossum',
        }

    def _get_post_response(self, data):
        return self.client.post(
            self.PATH, json.dumps(data), content_type='application/json'
        )

    def _create_superuser(self):
        self.super_user = CustomUser.objects.create_superuser(
            **self.valid_data
        )


class TestRegisterUser(UserTestMixin):
    """ Test module for register users """

    PATH = '/register/'

    def test_bad_request(self):
        response = self._get_post_response({})
        for key in (self.EMAIL, self.USERNAME, self.PASSWORD):
            self.assertEqual(response.data[key][0], 'This field is required.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_email_not_valid(self):
        error_data = self.valid_data.copy()
        error_data[self.EMAIL] = 123
        response = self._get_post_response(error_data)
        self.assertEqual(
            response.data[self.EMAIL][0], 'Enter a valid email address.'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_register_user(self):
        response = self._get_post_response(self.valid_data)

        user = CustomUser.objects.first()
        serializer = UserRegisterationSerializer(user)
        for key, value in serializer.data.items():
            self.assertEqual(
                response.data[key], serializer.data[key]
            )
        self.assertIn(self.TOKENS, response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestLoginUser(UserTestMixin):
    """ Test module for login users """

    PATH = '/login/'

    def test_incorrect_credentials(self):
        response = self._get_post_response(self.valid_data)
        self.assertEqual(
            response.data['non_field_errors'][0], 'Incorrect Credentials'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_login_user(self):
        self._create_superuser()
        response = self._get_post_response(self.valid_data)

        user = CustomUser.objects.first()
        serializer = UserLoginSerializer(user)
        self.assertEqual(
                response.data[self.EMAIL], serializer.data[self.EMAIL]
            )
        self.assertIn(self.TOKENS, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTokenRefreshUser(UserTestMixin):
    """ Test module for refresh token """

    PATH = '/token/refresh/'

    def test_bad_request(self):
        response = self._get_post_response({})
        self.assertEqual(
            response.data[self.REFRESH][0], 'This field is required.'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_not_valid(self):
        response = self._get_post_response({'refresh': 123})
        self.assertEqual(
            response.data['detail'], 'Token is invalid or expired'
        )
        self.assertEqual(
            response.data['code'], 'token_not_valid'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_refresh_token(self):
        register_response = self.client.post(
            '/register/',
            json.dumps(self.valid_data),
            content_type='application/json'
        )
        response = self._get_post_response(
            {self.REFRESH: register_response.data[self.TOKENS][self.REFRESH]}
        )

        self.assertIn(self.ACCESS, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogoutUser(UserTestMixin):
    """ Test module for logout useer """

    PATH = '/logout/'

    def setUp(self) -> None:
        super().setUp()
        self._create_superuser()
        self.client.force_login(self.super_user)

    def test_bad_request(self):
        response = self._get_post_response({})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_success_logout(self):
        login_response = self.client.post(
            '/login/',
            json.dumps(self.valid_data),
            content_type='application/json'
        )
        response = self._get_post_response(login_response.data[self.TOKENS])

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)


class TestUserAPIView(UserTestMixin):
    """ Test module for useer API """

    PATH = reverse('users:user-info')

    def setUp(self) -> None:
        super().setUp()
        self.new_name = 'Rob'
        self._create_superuser()
        self.client.force_login(self.super_user)

    def test_not_allowed(self):
        response = self._get_post_response({})
        self.assertEqual(
            response.data['detail'], 'Method "POST" not allowed.'
        )
        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_get_user(self):
        response = self.client.get(self.PATH)

        user = CustomUser.objects.first()
        serializer = CustomUserSerializer(user)
        for key, value in serializer.data.items():
            self.assertEqual(
                response.data[key], serializer.data[key]
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_user(self):
        new_email = '123@123.com'
        new_data = {
            self.USERNAME: self.new_name,
            self.EMAIL: new_email,
        }

        response = self.client.put(
            self.PATH, json.dumps(new_data), content_type='application/json'
        )

        user = CustomUser.objects.first()
        self.assertEqual(user.username, self.new_name)
        self.assertEqual(user.email, new_email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_user(self):
        new_data = {self.USERNAME: self.new_name}
        response = self.client.patch(
            self.PATH, json.dumps(new_data), content_type='application/json'
        )

        user = CustomUser.objects.get(username=self.new_name)
        self.assertEqual(user.username, self.new_name)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
