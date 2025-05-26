from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.contrib.admin.widgets import AdminTextareaWidget
from .models import Comment

class CustomTextareaWidget(AdminTextareaWidget):
    def __init__(self, attrs=None):
        default_attrs = {'rows': '8', 'cols': '80', 'style': 'font-family: monospace; line-height: 1.5;'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'author_display', 'short_content', 'content_object_display', 'has_parent',
        'data_processing_agreed', 'has_code', 'created_at'
    )
    list_filter = ('created_at', 'data_processing_agreed', 'content_type', 'has_code')
    search_fields = ('content', 'author_name', 'user__username')
    readonly_fields = ('created_at', 'content_type', 'object_id', 'content_object_display', 'user')
    raw_id_fields = ('parent',)

    formfield_overrides = {
        models.TextField: {'widget': CustomTextareaWidget},
    }

    fieldsets = (
        (None, {
            'fields': ('content', 'author_name', 'user')
        }),
        ('Код', {
            'fields': ('has_code', 'code', 'code_language'),
            'classes': ('collapse',),
        }),
        ('Зв\'язки', {
            'fields': ('parent', 'content_type', 'object_id', 'content_object_display'),
            'classes': ('collapse-open',),
        }),
        ('Налаштування', {
            'fields': ('created_at', 'data_processing_agreed'),
            'classes': ('collapse',),
        }),
    )

    def short_content(self, obj):
        if len(obj.content) > 80:
            return obj.content[:77] + '...'
        return obj.content

    short_content.short_description = 'Коментар'

    def author_display(self, obj):
        if obj.user:
            return format_html('<strong>{}</strong> ({})', obj.author_name, obj.user.username)
        return obj.author_name

    author_display.short_description = 'Автор'

    def content_object_display(self, obj):
        if obj.content_type and obj.object_id:
            content_type = obj.content_type
            model_class = content_type.model_class()
            if model_class is None:
                # Тип моделі вже не існує в проекті
                return f"{content_type.name}: (модель видалено, ID:{obj.object_id})"
            try:
                instance = model_class.objects.get(id=obj.object_id)
                if hasattr(instance, 'title'):
                    return format_html('{}: <a href="/admin/{}/{}/{}/change/">{}</a>',
                                       content_type.name,
                                       content_type.app_label,
                                       content_type.model,
                                       obj.object_id,
                                       instance.title)
                return format_html('{}: <a href="/admin/{}/{}/{}/change/">ID: {}</a>',
                                   content_type.name,
                                   content_type.app_label,
                                   content_type.model,
                                   obj.object_id,
                                   obj.object_id)

            except model_class.DoesNotExist:
                return f"{content_type.name}: (видалено, ID:{obj.object_id})"
        return '-'

    content_object_display.short_description = 'Прикріплено до'

    def has_parent(self, obj):
        return bool(obj.parent)

    has_parent.boolean = True
    has_parent.short_description = 'Відповідь'