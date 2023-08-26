import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    token_created_at = models.DateTimeField(auto_now=True)