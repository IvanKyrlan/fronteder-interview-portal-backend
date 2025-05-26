from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimestampedModel

class ForumTopic(TimestampedModel):
    CATEGORY_CHOICES = [
        ('technical', 'Технічні питання'),
        ('interview', 'Питання до співбесід'),
        ('career', 'Кар\'єра'),
        ('other', 'Інше'),
    ]

    title = models.CharField(max_length=255, verbose_name="Заголовок теми")
    content = models.TextField(verbose_name="Зміст теми")
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='other', 
        verbose_name="Категорія"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="forum_topics", 
        verbose_name="Автор"
    )
    views = models.PositiveIntegerField(default=0, verbose_name="Кількість переглядів")
    is_pinned = models.BooleanField(default=False, verbose_name="Закріплена тема")

    likes = models.ManyToManyField(
        User, 
        related_name="liked_topics", 
        blank=True, 
        verbose_name="Лайки"
    )
    bookmarks = models.ManyToManyField(
        User, 
        related_name="bookmarked_topics", 
        blank=True, 
        verbose_name="Закладки"
    )
    has_code = models.BooleanField(default=False, verbose_name="Містить код")

    comments = GenericRelation('comments.Comment', related_query_name='forum_topic')

    class Meta:
        verbose_name = "Тема форуму"
        verbose_name_plural = "Теми форуму"
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title