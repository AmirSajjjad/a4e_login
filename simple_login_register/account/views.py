from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from random import randint


from .serializers import CheckPhoneNumberRequestSerializer, TokenSerializer
from .models import User


def check_user_is_limited(phone_number):
    # TODO check user IP 
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
    print(code)
    # TODO *** sending otp code with celery task ***

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def give_warning_to_user(phone_number):
    # TODO warning to ip
    cache_key = f"{phone_number}-warning_count"
    warning = cache.get(cache_key)
    if warning.isdigit:
        warning = warning + 1
    else:
        warning = 1
    cache.set(cache_key, warning, settings.USER_LIMIT_TIME)

def check_OTP_code(phone_number, code):
    cache_key = f"{phone_number}-OTP"
    valid_otp_code = cache.get(cache_key)
    if not valid_otp_code:
        # TODO only warning to IP or use give_warning_to_user function?
        raise "otp code not find"
    if valid_otp_code != code:
        give_warning_to_user(phone_number)
        raise "invalid otp code"
        

class CheckPhoneNumberView(APIView):
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


class CheckPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = kwargs.pop("phone_number", None)
        password = kwargs.pop("password", None)

        serializer = CheckPhoneNumberRequestSerializer(data={"phone_number": phone_number})
        serializer.is_valid(raise_exception=True)

        if check_user_is_limited(phone_number):
            raise "User Is Limited"
        
        user = authenticate(request, username=phone_number, password=password)
        if user is None:
            give_warning_to_user(phone_number)
            raise "Invalid phone number or Password"
        
        password_serializer = TokenSerializer(data=get_tokens_for_user(user))
        return Response(password_serializer.data)


class CheckOTPView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = kwargs.pop("phone_number", None)
        code = kwargs.pop("code", None)

        serializer = CheckPhoneNumberRequestSerializer(data={"phone_number": phone_number})
        serializer.is_valid(raise_exception=True)

        if check_user_is_limited(phone_number):
            raise "User Is Limited"
        
        check_OTP_code(phone_number, code)

        # Using get_or_create for create a new user or generate token for an existing user to reset password or ...
        user = User.objects.get_or_create(phone_number=phone_number)
        password_serializer = TokenSerializer(data=get_tokens_for_user(user))
        return Response(password_serializer.data)
