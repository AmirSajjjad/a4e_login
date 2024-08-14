from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView

from .utils import (
    send_otp_code,
    get_tokens_for_user,
    give_warning_to_user,
    check_OTP_code,
)
from .serializers import CheckPhoneNumberRequestSerializer, TokenSerializer, UpdateProfileSerializer
from .models import User


class CheckPhoneNumberView(APIView):
    def get(self, request,*args, **kwargs):
        phone_number = self.request.query_params.get('phone_number')

        serializer = CheckPhoneNumberRequestSerializer(data={"phone_number": phone_number})
        serializer.is_valid(raise_exception=True)

        user_instance = User.objects.filter(phone_number__iexact=phone_number)
        if user_instance.exists():
            return Response(data="Send password")
        else:
            send_otp_code(phone_number)
            return Response(data="Send OTP Code")


class CheckPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = kwargs.pop("phone_number", None)
        password = kwargs.pop("password", None)

        serializer = CheckPhoneNumberRequestSerializer(data={"phone_number": phone_number})
        serializer.is_valid(raise_exception=True)
        
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
        
        check_OTP_code(phone_number, code)

        # Using get_or_create for create a new user or generate token for an existing user to reset password or ...
        user = User.objects.get_or_create(phone_number=phone_number)
        password_serializer = TokenSerializer(data=get_tokens_for_user(user))
        return Response(password_serializer.data)


class UpdateUserProfileView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateProfileSerializer
    lookup_field = None
    
    def get_object(self):
        return self.request.user
