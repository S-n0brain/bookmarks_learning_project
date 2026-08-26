from django.contrib.auth.models import User
from django.http import HttpRequest

from account.models import Profile


def create_profile(backend, user, *args, **kwargs):
    """
    Создать профиль пользователя для социальной аутентификации
    """
    Profile.objects.get_or_create(user=user)


class EmailAuthBackend:
    def authenticate(self, request: HttpRequest, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(raw_password=password):
                return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
