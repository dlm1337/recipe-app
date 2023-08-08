import os
import uuid
from .forms import CustomUserCreationForm
from django.test import TestCase, override_settings
from .models import CustomUser
from django.core.files import File
from django.shortcuts import reverse


class CustomUserModelTest(TestCase):
    def setUp(self):
        # Create a test user for the model
        self.test_user = CustomUser.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            about_me="I am a test user.",
            favorite_food="Pizza",
            pic="fsfsgsrgsgsrgsrgsrgsrg",
        )

    def test_model_str(self):
        # Test the __str__ method of the model
        self.assertEqual(str(self.test_user), "testuser")

    def test_model_pic_field_default(self):
        # Test the default value for the pic field
        default_pic = "fsfsgsrgsgsrgsrgsrgsrg"
        self.assertEqual(self.test_user.pic, default_pic)

    def test_model_about_me_field(self):
        # Test the about_me field
        self.assertEqual(self.test_user.about_me, "I am a test user.")

    def test_model_favorite_food_field(self):
        # Test the favorite_food field
        self.assertEqual(self.test_user.favorite_food, "Pizza")

    def test_pic_field(self):
        user = self.test_user
        self.assertEqual(user.pic, "fsfsgsrgsgsrgsrgsrgsrg")

    def test_model_user_creation(self):
        # Test user creation
        user = CustomUser.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="newpassword",
            about_me="I am a new user.",
            favorite_food="Sushi",
        )
        self.assertIsInstance(user, CustomUser)
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertTrue(user.check_password("newpassword"))

    def test_success_view(self):
        # Test GET request to the success view
        response = self.client.get(reverse("success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customuser/success.html")


class CustomUserViewTest(TestCase):
    def test_register_user_view(self):
        # Test GET request to the register_user view
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "customuser/register.html")
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

        # Test POST request with valid data
        data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "about_me": "I am a test user.",
            "favorite_food": "Pizza",
            "submit_type": "register_btn",
        }
        response = self.client.post(reverse("register"), data, follow=True)

        # Ensure that the user is created in the database
        self.assertTrue(CustomUser.objects.filter(username="testuser").exists())
