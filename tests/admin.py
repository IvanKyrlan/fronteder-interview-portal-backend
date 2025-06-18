from django.contrib import admin
from django.db import models
from .models import Test, Question, Answer, UserProgress, TestAttempt
from django.contrib.admin.widgets import AdminTextareaWidget

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 4
    min_num = 4
    validate_min = True

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'text':
            formfield.widget.attrs.update({
                'required': 'required',
                'placeholder': 'Введіть варіант відповіді',
            })
        return formfield


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('test', 'question_preview', 'correct_answer', 'created_at')
    list_filter = ('test',)
    search_fields = ('question',)
    inlines = [AnswerInline]

    def question_preview(self, obj):
        return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question

    def correct_answer(self, obj):
        correct = obj.answers.filter(is_correct=True).first()
        if correct:
            return correct.text[:30] + '...' if len(correct.text) > 30 else correct.text
        return "Немає правильної відповіді"

    question_preview.short_description = 'Питання'
    correct_answer.short_description = 'Правильна відповідь'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not obj.answers.filter(is_correct=True).exists():
            first_answer = obj.answers.first()
            if first_answer:
                first_answer.is_correct = True
                first_answer.save()
                self.message_user(request, 'Автоматично встановлено першу відповідь як правильну.')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        correct_count = 0

        for instance in instances:
            if hasattr(instance, 'is_correct') and instance.is_correct:
                correct_count += 1

        if correct_count > 1:
            self.message_user(request, 'Увага: Буде збережена тільки одна правильна відповідь!', level='WARNING')

        if correct_count == 0 and instances:
            instances[0].is_correct = True
            self.message_user(request,
                             'Автоматично встановлено першу відповідь як правильну, оскільки не вказано правильної відповіді.')

        for instance in instances:
            if hasattr(instance, 'text') and instance.text.strip():
                instance.save()

        formset.save_m2m()


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'questions', 'description', 'duration', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    ordering = ('id',)
    list_editable = ('questions', 'duration', 'description')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'completed_at')
    list_filter = ('test', 'completed_at')
    search_fields = ('user__username', 'test__title')
    raw_id_fields = ('user', 'test')

@admin.register(TestAttempt)
class TestAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'correct_answers', 'total_questions', 'completed_at')
    list_filter = ('test', 'user')
    search_fields = ('user__username', 'test__title')
    readonly_fields = ('user', 'test', 'score', 'correct_answers', 'total_questions', 'completed_at', 'progress')