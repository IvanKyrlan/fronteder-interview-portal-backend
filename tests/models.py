from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from core.models import TimestampedModel


class Test(TimestampedModel):
    ICON_CHOICES = [
        ('DiHtml5', 'HTML5'),
        ('DiCss3', 'CSS3'),
        ('DiJsBadge', 'JavaScript'),
        ('DiReact', 'React'),
        ('DiDatabase', 'Database/SQL'),
        ('DiDjango', 'Django'),
    ]

    COLOR_CHOICES = [
        ('text-orange-500', 'Orange'),
        ('text-blue-500', 'Blue'),
        ('text-yellow-400', 'Yellow'),
        ('text-blue-400', 'Light Blue'),
        ('text-blue-600', 'Dark Blue'),
        ('text-green-500', 'Green'),
        ('text-purple-500', 'Purple'),
        ('text-red-500', 'Red'),
        ('text-gray-500', 'Gray'),
    ]

    title = models.CharField(max_length=200, verbose_name="Назва")
    description = models.TextField(verbose_name="Опис")
    duration = models.IntegerField(verbose_name="Тривалість (хв)")
    questions = models.IntegerField(default=30, verbose_name="Кількість питань")
    icon = models.CharField(
        max_length=50,
        choices=ICON_CHOICES,
        default='DiJsBadge',
        verbose_name="Іконка"
    )
    color = models.CharField(
        max_length=50,
        choices=COLOR_CHOICES,
        default='text-gray-500',
        verbose_name="Колір"
    )
    comments = GenericRelation('comments.Comment', related_query_name='test')

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тести'
        ordering = ['id']

    def __str__(self):
        return self.title


class Question(TimestampedModel):
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='test_questions',
        verbose_name="Тест"
    )
    question = models.TextField(verbose_name="Питання")

    class Meta:
        verbose_name = 'Питання для тестів'
        verbose_name_plural = 'Питання для тестів'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.test.title} - {self.question[:50]}..."

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        correct_answers = self.answers.filter(is_correct=True)
        if correct_answers.count() > 1:
            first_correct = correct_answers.first()
            for answer in correct_answers.exclude(id=first_correct.id):
                answer.is_correct = False
                answer.save()


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Питання"
    )
    text = models.TextField(verbose_name="Текст відповіді")
    is_correct = models.BooleanField(default=False, verbose_name="Правильна відповідь")

    class Meta:
        verbose_name = 'Відповідь'
        verbose_name_plural = 'Відповіді'

    def __str__(self):
        return f"{self.text[:50]}... ({'Правильно' if self.is_correct else 'Неправильно'})"

    def save(self, *args, **kwargs):
        if not self.text.strip():
            return

        if self.is_correct:
            self.question.answers.exclude(id=self.id).update(is_correct=False)

        super().save(*args, **kwargs)

        if not self.question.answers.filter(is_correct=True).exists():
            first_answer = self.question.answers.first()
            if first_answer:
                first_answer.is_correct = True
                first_answer.save(update_fields=['is_correct'])


class UserProgress(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name="Користувач"
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name="Тест"
    )
    score = models.IntegerField(verbose_name="Результат (%)")
    attempts = models.IntegerField(default=0, verbose_name="Кількість спроб")
    completed_at = models.DateTimeField(auto_now=True, verbose_name="Дата завершення")

    class Meta:
        verbose_name = 'Прогрес тесту'
        verbose_name_plural = 'Прогрес тестів'
        ordering = ['-completed_at']
        unique_together = ['user', 'test']

    def __str__(self):
        return f"{self.user.username} - {self.test.title}: {self.score}% ({self.attempts} спроб)"


class TestAttempt(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='test_attempts',
        verbose_name="Користувач"
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Тест"
    )
    score = models.IntegerField(verbose_name="Результат (%)")
    correct_answers = models.IntegerField(verbose_name="Правильні відповіді")
    total_questions = models.IntegerField(verbose_name="Загальна кількість питань")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завершення")

    progress = models.ForeignKey(
        UserProgress,
        on_delete=models.CASCADE,
        related_name='test_history',
        null=True,
        verbose_name="Прогрес"
    )

    class Meta:
        verbose_name = 'Спроба тесту'
        verbose_name_plural = 'Спроби тестів'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user.username} - {self.test.title}: {self.score}% ({self.correct_answers}/{self.total_questions})"

    def save(self, *args, **kwargs):
        progress, created = UserProgress.objects.get_or_create(
            user=self.user,
            test=self.test,
            defaults={'score': self.score, 'attempts': 1}
        )

        if not created:
            progress.score = self.score
            progress.attempts += 1
            progress.save()

        self.progress = progress
        super().save(*args, **kwargs)