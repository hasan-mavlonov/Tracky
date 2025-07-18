from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
import logging
logger = logging.getLogger(__name__)

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        logger.debug(f"Attempting to authenticate: {username}")
        try:
            user = UserModel.objects.get(phone_number=username)
            if user.check_password(password):
                logger.debug(f"Password valid for {username}")
                if self.user_can_authenticate(user):
                    logger.debug(f"User {username} is active and authenticated")
                    return user
                else:
                    logger.debug(f"User {username} is not active")
            else:
                logger.debug(f"Password invalid for {username}")
        except UserModel.DoesNotExist:
            logger.debug(f"User {username} not found")
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None