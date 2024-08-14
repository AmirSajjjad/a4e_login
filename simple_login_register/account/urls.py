from django.urls import path

from .views import CheckPhoneNumberView

urlpatterns = [
    path('login/check_phone_number', CheckPhoneNumberView.as_view(), name="check-phone-number"),
]
