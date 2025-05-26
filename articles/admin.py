from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.contrib.admin.widgets import AdminTextareaWidget
from .models import Article, ArticleSection

class CustomTextareaWidget(AdminTextareaWidget):
    def __init__(self, attrs=None):
        default_attrs = {'rows': '12', 'cols': '80', 'style': 'font-family: monospace; line-height: 1.5;'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class ArticleSectionInline(admin.StackedInline):
    model = ArticleSection
    extra = 0
    classes = ('collapse-open',)

    fieldsets = (
        (None, {
            'fields': ('order', 'title'),
        }),
        ('Вміст секції', {
            'fields': ('content', 'image', 'image_caption', 'code', 'language', 'code_description'),
            'classes': ('collapse-open',),
            'description': format_html(
                'Кожна секція може містити будь-яку комбінацію тексту, зображення та коду.<br><br>'
                '<strong style="background-color: #f8f8f8; padding: 3px 6px; border: 1px solid #ddd; border-radius: 3px;">HTML-форматування:</strong><br>'
                '- Жирний текст: &lt;strong&gt;текст&lt;/strong&gt;<br>'
                '- Курсив: &lt;em&gt;текст&lt;/em&gt;<br>'
                '- Перенос рядка: &lt;br&gt;'
            ),
        }),
    )

    formfield_overrides = {
        models.TextField: {'widget': CustomTextareaWidget},
    }


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'article_type', 'author', 'published_at', 'updated_at', 'featured')
    list_filter = ('article_type', 'featured', 'published_at')
    search_fields = ('title', 'description', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleSectionInline]
    date_hierarchy = 'published_at'

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'article_type', 'author')
        }),
        ('Контент', {
            'fields': ('thumbnail', 'description', 'summary'),
            'classes': ('collapse-open',),
            'description': format_html(
                'Підтримується HTML-форматування.<br><br>'
                '<strong style="background-color: #f8f8f8; padding: 3px 6px; border: 1px solid #ddd; border-radius: 3px;">Приклади форматування:</strong><br>'
                '- Жирний текст: &lt;strong&gt;текст&lt;/strong&gt;<br>'
                '- Курсив: &lt;em&gt;текст&lt;/em&gt;<br>'
                '- Перенос рядка: &lt;br&gt;'
            ),
        }),
        ('Налаштування', {
            'fields': ('published_at', 'featured'),
            'classes': ('collapse',)
        }),
    )

    formfield_overrides = {
        models.TextField: {'widget': CustomTextareaWidget},
    }

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)