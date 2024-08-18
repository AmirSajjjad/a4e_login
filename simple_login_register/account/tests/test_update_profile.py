from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.test import APITestCase
from account.models import User


class TestCheckPassword(APITestCase):

    def setUp(self) -> None:
        self.phone_number = "+999999999"
        self.url = "/account/profile/update"
        
        self.user = User.objects.create(phone_number=self.phone_number)
        
        self.data = {
            "password" : "123",
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "email@email.email",
        }
    
    def test_not_autenticate(self):
        response = self.client.put(self.url)
        response_data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response_data["detail"], 'Authentication credentials were not provided.')

    def test_ok(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, data=self.data)
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(self.user.first_name, self.data["first_name"])
        self.assertEqual(self.user.last_name, self.data["last_name"])
        self.assertEqual(self.user.email, self.data["email"])

        self.assertIsNotNone(authenticate(phone_number=self.phone_number , password=self.data["password"]))
        