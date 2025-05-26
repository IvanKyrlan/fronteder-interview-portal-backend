from django.contrib import admin
from django.db import models
from .models import InteractiveTask, TaskSolution, TaskAttempt, UserTaskProgress

class TaskSolutionInline(admin.TabularInline):
    model = TaskSolution
    extra = 1
    min_num = 1
    max_num = 5


@admin.register(InteractiveTask)
class InteractiveTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'test', 'task_type', 'difficulty', 'created_at')
    list_filter = ('test', 'task_type', 'difficulty')
    search_fields = ('title', 'description', 'initial_code')
    inlines = [TaskSolutionInline]

    fieldsets = (
        (None, {
            'fields': ('test', 'title', 'description')
        }),
        ('Код', {
            'fields': ('initial_code', 'task_type')
        }),
        ('Додатково', {
            'fields': ('difficulty',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['initial_code'].widget.attrs['style'] = 'font-family: monospace; width: 100%; height: 300px;'
        return form


@admin.register(TaskAttempt)
class TaskAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'is_correct', 'completed_at')
    list_filter = ('is_correct', 'task__test', 'user')
    search_fields = ('user__username', 'task__title', 'submitted_code')
    readonly_fields = ('user', 'task', 'submitted_code', 'is_correct', 'completed_at')


@admin.register(UserTaskProgress)
class UserTaskProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'completed_tasks', 'total_tasks', 'last_updated')
    list_filter = ('test',)
    search_fields = ('user__username', 'test__title')