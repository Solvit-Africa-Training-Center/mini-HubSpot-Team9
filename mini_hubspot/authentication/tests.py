from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer

UserModel = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "sales_rep",
        }

    def test_create_user(self):
        user = User.objects.create_user(**self.user_data)
        user.set_password(self.user_data["password"])
        user.save()
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "sales_rep")
        self.assertTrue(user.check_password("testpass123"))

    def test_create_superuser(self):
        admin_data = self.user_data.copy()
        admin_data["username"] = "admin"
        admin_data["email"] = "admin@example.com"
        admin_data["role"] = "admin"  # Explicitly set role to admin
        user = User.objects.create_superuser(**admin_data)
        self.assertEqual(user.role, "admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.refresh_url = reverse("token_refresh")

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User",
            "role": "sales_rep",
        }
        self.user = User.objects.create_user(**self.user_data)
        self.user.set_password(self.user_data["password"])
        self.user.save()

    def test_user_registration_success(self):
        new_user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "testpassword123",
            "password_confirm": "testpassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "sales_rep",
        }
        response = self.client.post(self.register_url, new_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])
        self.assertIn("user", response.data)
        user = User.objects.get(username="newuser")
        self.assertEqual(user.role, "sales_rep")

    def test_user_login_success(self):
        login_data = {"username": "testuser", "password": "testpass123"}
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_user_login_invalid_credentials(self):
        invalid_data = {"username": "testuser", "password": "wrongpass"}
        response = self.client.post(self.login_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_login_nonexistent_user(self):
        invalid_data = {"username": "noone", "password": "nopass"}
        response = self.client.post(self.login_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh_success(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(self.refresh_url, {"refresh": str(refresh)}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)
        self.assertIn("access", response.data["tokens"])
        self.assertIn("refresh", response.data["tokens"])

    def test_token_refresh_invalid_token(self):
        response = self.client.post(self.refresh_url, {"refresh": "invalidtoken"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)