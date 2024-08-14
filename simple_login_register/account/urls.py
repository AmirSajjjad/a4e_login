from django.urls import path

from .views import CheckPhoneNumberView, CheckPasswordView, CheckOTPView, UpdateUserProfileView

urlpatterns = [
    path('login/check_phone_number', CheckPhoneNumberView.as_view(), name="check-phone-number"),
    path('login/check_password', CheckPasswordView.as_view(), name="check-password"),
    path('login/check_otp', CheckOTPView.as_view(), name="check-otp"),
    path('profile/update', UpdateUserProfileView.as_view(), name="profile-update"),
]
