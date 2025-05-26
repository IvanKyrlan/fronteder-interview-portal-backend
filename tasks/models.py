from django.db import models
from django.contrib.auth.models import User
from core.models import TimestampedModel
from tests.models import Test

class InteractiveTask(TimestampedModel):
    TASK_TYPE_CHOICES = [
        ('complete', 'Дописати код'),
        ('fill_gap', 'Заповнити пропуск'),
        ('fix_bug', 'Виправити помилку'),
    ]

    test = models.ForeignKey(
        Test, 
        on_delete=models.CASCADE, 
        related_name='interactive_tasks',
        verbose_name="Тест"
    )
    title = models.CharField(max_length=200, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    initial_code = models.TextField(
        help_text="Початковий код завдання",
        verbose_name="Початковий код"
    )
    task_type = models.CharField(
        max_length=20, 
        choices=TASK_TYPE_CHOICES, 
        default='complete',
        verbose_name="Тип завдання"
    )
    difficulty = models.IntegerField(
        default=1, 
        help_text="Рівень складності від 1 до 5",
        verbose_name="Складність"
    )

    class Meta:
        verbose_name = 'Інтерактивне завдання'
        verbose_name_plural = 'Інтерактивні завдання'
        ordering = ['test', 'difficulty', 'created_at']

    def __str__(self):
        return f"{self.test.title} - {self.title}"

    def save(self, *args, **kwargs):
        self.initial_code = self.initial_code.replace('\\n', '\n')
        super().save(*args, **kwargs)

class TaskSolution(models.Model):
    task = models.ForeignKey(
        InteractiveTask, 
        on_delete=models.CASCADE, 
        related_name='solutions',
        verbose_name="Завдання"
    )
    solution_code = models.TextField(
        help_text="Правильний варіант рішення",
        verbose_name="Код рішення"
    )
    is_primary = models.BooleanField(
        default=False, 
        help_text="Чи це основне рішення",
        verbose_name="Основне рішення"
    )
    hint = models.TextField(
        blank=True, 
        null=True, 
        help_text="Підказка для цього рішення",
        verbose_name="Підказка"
    )

    class Meta:
        verbose_name = 'Рішення завдання'
        verbose_name_plural = 'Рішення завдань'

    def __str__(self):
        return f"Рішення для {self.task.title} ({'Основне' if self.is_primary else 'Альтернативне'})"

class TaskAttempt(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='task_attempts',
        verbose_name="Користувач"
    )
    task = models.ForeignKey(
        InteractiveTask, 
        on_delete=models.CASCADE, 
        related_name='attempts',
        verbose_name="Завдання"
    )
    submitted_code = models.TextField(verbose_name="Відправлений код")
    is_correct = models.BooleanField(verbose_name="Правильно")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завершення")

    class Meta:
        verbose_name = 'Спроба інтерактивного завдання'
        verbose_name_plural = 'Спроби інтерактивних завдань'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.task.title} - {'Успішно' if self.is_correct else 'Невдало'}"

class UserTaskProgress(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='task_progress',
        verbose_name="Користувач"
    )
    test = models.ForeignKey(
        Test, 
        on_delete=models.CASCADE, 
        related_name='user_task_progress',
        verbose_name="Тест"
    )
    completed_tasks = models.IntegerField(default=0, verbose_name="Виконані завдання")
    total_tasks = models.IntegerField(default=0, verbose_name="Загальна кількість завдань")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Останнє оновлення")

    class Meta:
        verbose_name = 'Прогрес інтерактивних завдань'
        verbose_name_plural = 'Прогрес інтерактивних завдань'
        unique_together = ['user', 'test']

    def __str__(self):
        return f"{self.user.username} - {self.test.title}: {self.completed_tasks}/{self.total_tasks}"