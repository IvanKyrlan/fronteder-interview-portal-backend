from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from core.models import TimestampedModel


class Comment(TimestampedModel):
    content = models.TextField(verbose_name="Коментар")
    author_name = models.CharField(max_length=100, verbose_name="Ім'я автора")

    code = models.TextField(blank=True, null=True, verbose_name="Код")
    code_language = models.CharField(max_length=20, blank=True, null=True, verbose_name="Мова коду")
    has_code = models.BooleanField(default=False, verbose_name="Містить код")

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments",
        verbose_name="Користувач"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name="Батьківський коментар"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Тип контенту")
    object_id = models.PositiveIntegerField(verbose_name="ID об'єкту")
    content_object = GenericForeignKey('content_type', 'object_id')

    data_processing_agreed = models.BooleanField(default=False, verbose_name="Згода на обробку даних")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.author_name}: {self.content[:50]}..."