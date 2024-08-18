from django.core.cache import cache
from django.conf import settings
from rest_framework.test import APITestCase


class TestCheckPassword(APITestCase):

    def setUp(self) -> None:
        self.invalid_phone_number = "+99999999"
        self.phone_number = "+999999999"
        self.url = "/account/login/check_otp"
        
        self.user_warning_cache_key = self.phone_number + settings.CACHE_WARNING_KEY
        cache.delete(self.user_warning_cache_key)
        self.user_otp_cache_key = self.phone_number + settings.CACHE_OTP_KEY
        cache.delete(self.user_otp_cache_key)

    def test_invalid_inputs(self):
        # dont send any parameters
        response = self.client.post(self.url)
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["phone_number"], ['This field may not be null.'])
        cache.delete(self.user_otp_cache_key)
        
        # send invalid number
        response = self.client.post(self.url, data={"phone_number": self.invalid_phone_number})
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data["phone_number"], ["Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."])

        # dont send otp code
        response = self.client.post(self.url, data={"phone_number": self.phone_number})
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, ["otp code not find"])
        self.assertEqual(cache.get(self.user_warning_cache_key), 1)

        # code not exists on cache
        response = self.client.post(self.url, data={"phone_number": self.phone_number, "code": 123})
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, ["otp code not find"])
        self.assertEqual(cache.get(self.user_warning_cache_key), 2)

        # send invalid otp code
        cache.set(self.user_otp_cache_key, "123")
        response = self.client.post(self.url, data={"phone_number": self.phone_number, "code": 321})
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data, ["invalid otp code"])
        self.assertEqual(cache.get(self.user_warning_cache_key), 3)

    def test_user_ip_limit(self):
        cache_key = self.phone_number + settings.CACHE_WARNING_KEY
        cache.set(cache_key, settings.MAX_USER_WARNING_COUNT + 1, settings.USER_LIMIT_TIME)
        cache.set(self.user_otp_cache_key, "123")
        
        response = self.client.post(self.url, data={"phone_number": self.phone_number, "code": 123})
        response_data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['phone_number'], ['User Is Limited'])
    
    def test_ok(self):
        cache.set(self.user_otp_cache_key, "123")
        response = self.client.post(self.url, data={"phone_number": self.phone_number, "code": 123})
        response_data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("refresh", response_data.keys())
        self.assertIn("access", response_data.keys())
