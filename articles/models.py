from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimestampedModel

class Article(TimestampedModel):
    TYPE_CHOICES = (
        ('news', 'Новина'),
        ('task', 'Завдання'),
    )

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(max_length=250, unique=True, blank=True, verbose_name="URL slug")
    article_type = models.CharField(
        max_length=10, 
        choices=TYPE_CHOICES, 
        default='news', 
        verbose_name="Тип статті"
    )
    description = models.TextField(
        verbose_name="Короткий опис",
        help_text="Короткий опис для списку статей. Підтримує HTML-теги.",
        null=True,
        blank=True
    )
    summary = models.TextField(
        verbose_name="Підсумок",
        help_text="Підсумковий текст наприкінці статті. Підтримує HTML-теги.",
        blank=True
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="articles", 
        verbose_name="Автор"
    )
    published_at = models.DateTimeField(verbose_name="Дата публікації")
    featured = models.BooleanField(default=False, verbose_name="Рекомендована стаття")
    thumbnail = models.ImageField(
        upload_to='articles/thumbnails/', 
        blank=True, 
        null=True,
        verbose_name="Головне зображення"
    )
    comments = GenericRelation('comments.Comment', related_query_name='article')

    class Meta:
        ordering = ['-published_at']
        verbose_name = "Стаття"
        verbose_name_plural = "Статті"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

class ArticleSection(models.Model):
    LANGUAGE_CHOICES = (
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('javascript', 'JavaScript'),
        ('jsx', 'React'),
        ('sql', 'SQL'),
        ('python', 'Python'),
    )

    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        related_name="sections", 
        verbose_name="Стаття"
    )
    order = models.PositiveSmallIntegerField(
        default=0, 
        verbose_name="Порядок відображення"
    )
    title = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Заголовок секції"
    )

    content = models.TextField(
        blank=True,
        verbose_name="Текстовий вміст",
        help_text="Підтримує HTML-теги."
    )
    image = models.ImageField(
        upload_to='articles/images/', 
        blank=True, 
        null=True, 
        verbose_name="Зображення"
    )
    image_caption = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Підпис до зображення"
    )
    code = models.TextField(blank=True, verbose_name="Код")
    language = models.CharField(
        max_length=20, 
        choices=LANGUAGE_CHOICES, 
        default='javascript',
        blank=True, 
        verbose_name="Мова програмування"
    )
    code_description = models.TextField(blank=True, verbose_name="Опис коду")

    class Meta:
        ordering = ['order']
        verbose_name = "Секція статті"
        verbose_name_plural = "Секції статей"

    def __str__(self):
        return f"Секція для {self.article.title} (#{self.order})"