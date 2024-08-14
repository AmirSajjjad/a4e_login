from django.urls import path

from .views import CheckPhoneNumberView, CheckPasswordView

urlpatterns = [
    path('login/check_phone_number', CheckPhoneNumberView.as_view(), name="check-phone-number"),
    path('login/check_password', CheckPasswordView.as_view(), name="check-password"),
]
