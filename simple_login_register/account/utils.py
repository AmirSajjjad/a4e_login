from django.core.cache import cache
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from random import randint

def check_user_is_limited(phone_number):
    # TODO check user IP 
    cache_key = phone_number + settings.CACHE_WARNING_KEY
    warning_count = cache.get(cache_key)
    if not warning_count:
        return False
    if warning_count > settings.MAX_USER_WARNING_COUNT:
        return True
    return False
    
def send_otp_code(phone_number):
    code = randint(100000, 999999)
    cache_key = phone_number + settings.CACHE_OTP_KEY
    if cache.get(cache_key):
        raise ValidationError("Last otp code is now active. plz wait...")
    cache.set(cache_key, str(code), 60*2)
    print(f"OTP code is: {code}")
    # TODO *** sending otp code with celery task ***

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def give_warning_to_user(phone_number):
    # TODO warning to ip
    cache_key = phone_number + settings.CACHE_WARNING_KEY
    warning = cache.get(cache_key)
    if warning == None:
        warning = 1
    else:
        warning = warning + 1
    cache.set(cache_key, warning, settings.USER_LIMIT_TIME)

def check_OTP_code(phone_number, code):
    cache_key = phone_number + settings.CACHE_OTP_KEY
    valid_otp_code = cache.get(cache_key)
    if not valid_otp_code:
        give_warning_to_user(phone_number)
        raise ValidationError("otp code not find")
    if valid_otp_code != code:
        give_warning_to_user(phone_number)
        raise ValidationError("invalid otp code")
    cache.delete(cache_key)
