from django.db import models
from django.contrib.auth.models import User
from core.models import TimestampedModel


class UserProfile(TimestampedModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name="Користувач"
    )
    bio = models.TextField(blank=True, null=True, verbose_name="Біографія")
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар"
    )

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"

    def __str__(self):
        return f"Профіль: {self.user.username}"