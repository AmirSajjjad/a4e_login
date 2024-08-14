from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from random import randint

from .serializers import CheckPhoneNumberRequestSerializer
from .models import User


def check_user_is_limited(phone_number):
    cache_key = f"{phone_number}-warning_count"
    warning_count = cache.get(cache_key)
    if not warning_count:
        return False
    if warning_count > settings.MAX_USER_WARNING_COUNT:
        return False
    else:
        return True
    
def send_otp_code(phone_number):
    code = randint(100000, 999999)
    cache_key = f"{phone_number}-OTP"
    if cache.get(cache_key):
        raise "Last otp code is now active. plz wait..."
    cache.set(cache_key, code, 60*2)
    # TODO *** sending otp code with celery task ***


class CheckPhoneNumberView(APIView):
    serializer_class = CheckPhoneNumberRequestSerializer

    def get(self, request,*args, **kwargs):
        message = ""
        phone_number = self.request.query_params.get('phone_number')
        serializer = CheckPhoneNumberRequestSerializer(data={"phone_number": phone_number})
        serializer.is_valid(raise_exception=True)

        if check_user_is_limited(phone_number):
            raise "User Is Limited"

        user_instance = User.objects.filter(phone_number__iexact=phone_number)
        if user_instance.exists():
            message = "Send password"
        else:
            send_otp_code(phone_number)
            message = "Send OTP Code"

        return Response(data=message)
