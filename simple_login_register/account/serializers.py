from rest_framework import serializers
from django.core.validators import RegexValidator


phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

class CheckPhoneNumberRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[phone_regex],)
