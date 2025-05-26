from django.db import models
from core.models import TimestampedModel

class InterviewVideo(TimestampedModel):
    CATEGORY_CHOICES = [
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('fullstack', 'Full Stack'),
        ('devops', 'DevOps'),
        ('mobile', 'Mobile'),
        ('qa', 'QA'),
        ('other', 'Інше'),
    ]

    LEVEL_CHOICES = [
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
    ]

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    youtube_id = models.CharField(max_length=20, verbose_name="ID відео на YouTube")
    description = models.TextField(verbose_name="Опис")
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='frontend', 
        verbose_name="Категорія"
    )
    level = models.CharField(
        max_length=20, 
        choices=LEVEL_CHOICES, 
        default='junior', 
        verbose_name="Рівень"
    )
    featured = models.BooleanField(default=False, verbose_name="Рекомендоване")

    class Meta:
        verbose_name = "Відео співбесіди"
        verbose_name_plural = "Відео співбесід"
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return self.title