from django.contrib.auth.backends import BaseBackend
from .models import Account

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Accept email via username (Django admin sends it this way)
        try:
            user = Account.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Account.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Account.objects.get(pk=user_id)
        except Account.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        return getattr(user, 'is_active', False)
