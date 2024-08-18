from django.core.cache import cache
from django.conf import settings
from rest_framework.test import APITestCase
from account.models import User


class TestCheckPhoneNumber(APITestCase):

    def setUp(self) -> None:
        self.invalid_phone_number = "+99999999"
        self.phone_number = "+999999999"
        self.url = "/account/login/check_phone_number"
        
        self.user_warning_cache_key = self.phone_number + settings.CACHE_WARNING_KEY
        cache.delete(self.user_warning_cache_key)
        self.user_otp_cache_key = self.phone_number + settings.CACHE_OTP_KEY
        cache.delete(self.user_otp_cache_key)
    
    def test_invalid_inputs(self):
        # dont send any parameters
        response = self.client.get(self.url)
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["phone_number"], ['This field may not be null.'])
        cache.delete(self.user_otp_cache_key)
        
        # send invalid number
        response = self.client.get(self.url, data={"phone_number": self.invalid_phone_number})
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["phone_number"], ["Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."])
        
    def test_user_ip_limit(self):
        cache_key = self.phone_number + settings.CACHE_WARNING_KEY
        cache.set(cache_key, settings.MAX_USER_WARNING_COUNT + 1, settings.USER_LIMIT_TIME)

        response = self.client.get(self.url, data={"phone_number": self.phone_number})
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['phone_number'], ['User Is Limited'])

        # TODO: test ip limit:
        # cache.delete(cache_key)

    def test_ok_user_exists(self):
        User.objects.create(phone_number=self.phone_number)

        response = self.client.get(self.url, data={"phone_number": self.phone_number})
        response_data = response.json()
        print(response_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, "Send password")

    def test_ok_user_not_exists(self):
        response = self.client.get(self.url, data={"phone_number": self.phone_number})
        response_data = response.json()
        print(response_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data, "Send OTP Code")
        self.assertIsNotNone(cache.get(self.user_otp_cache_key))
