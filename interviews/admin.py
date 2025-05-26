from django.contrib import admin
from .models import InterviewVideo

@admin.register(InterviewVideo)
class InterviewVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'featured', 'created_at')
    list_filter = ('category', 'level', 'featured')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)