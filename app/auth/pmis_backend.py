import requests, json
from requests.auth import HTTPBasicAuth

from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User

class PMISBackend:

    def authenticate(self, request, username=None, password=None):
        auth_args = { '__RESPONSE_TYPE__': 'json' }
        r = requests.post(settings.PMIS_LOGIN_URL, data=auth_args, auth=HTTPBasicAuth(username, password))
        token = json.loads(r.text)

        login_valid = 'access_token' in token
        if login_valid:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. There's no need to set a password
                user = User(username=username)
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
