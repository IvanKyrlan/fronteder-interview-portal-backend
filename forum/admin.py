from django.contrib import admin
from .models import ForumTopic
from django.utils.html import format_html

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'views', 'is_pinned', 'comments_count')
    list_filter = ('category', 'is_pinned', 'created_at', 'has_code')
    search_fields = ('title', 'content', 'author__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('views', 'comments_count', 'created_at', 'updated_at')
    actions = ['pin_topics', 'unpin_topics']

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'category', 'author', 'is_pinned', 'has_code')
        }),
        ('Статистика', {
            'fields': ('views', 'comments_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def comments_count(self, obj):
        return obj.comments.count()

    comments_count.short_description = 'Коментарі'

    def pin_topics(self, request, queryset):
        queryset.update(is_pinned=True)
        self.message_user(request, f"{queryset.count()} тем було закріплено")

    pin_topics.short_description = "Закріпити вибрані теми"

    def unpin_topics(self, request, queryset):
        queryset.update(is_pinned=False)
        self.message_user(request, f"{queryset.count()} тем було відкріплено")

    unpin_topics.short_description = "Відкріпити вибрані теми"

    def save_model(self, request, obj, form, change):
        if "```" in obj.content:
            obj.has_code = True
        super().save_model(request, obj, form, change)