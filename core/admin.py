from django.contrib import admin
from django.contrib.admin.models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    readonly_fields = [f.name for f in LogEntry._meta.fields]  # не дозволяємо редагування
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag', 'change_message')
    list_filter = ('user', 'content_type', 'action_flag')
    search_fields = ('object_repr', 'change_message')
    ordering = ('-action_time',)

    def has_add_permission(self, request):
        return False  # забороняємо створення вручну
