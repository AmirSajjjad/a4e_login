from rest_framework import serializers
from django.core.validators import RegexValidator

from .models import User
from .utils import check_user_is_limited


phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")

class CheckPhoneNumberRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, validators=[phone_regex], required=True)

    def validate(self, attrs):
        if check_user_is_limited(attrs["phone_number"]):
            raise serializers.ValidationError("User Is Limited")
        return attrs


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()    


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "password",
            "first_name",
            "last_name",
            "email",
        ]
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)
