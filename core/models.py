# # core/models.py
#
# from django.db import models
# from django.contrib.auth.models import User
# from django.utils.text import slugify
# from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
# from django.contrib.contenttypes.models import ContentType
#
# class Test(models.Model):
#     ICON_CHOICES = [
#         ('DiHtml5', 'HTML5'),
#         ('DiCss3', 'CSS3'),
#         ('DiJsBadge', 'JavaScript'),
#         ('DiReact', 'React'),
#         ('DiDatabase', 'Database/SQL'),
#         ('DiDjango', 'Django'),
#     ]
#
#     COLOR_CHOICES = [
#         ('text-orange-500', 'Orange'),
#         ('text-blue-500', 'Blue'),
#         ('text-yellow-400', 'Yellow'),
#         ('text-blue-400', 'Light Blue'),
#         ('text-blue-600', 'Dark Blue'),
#         ('text-green-500', 'Green'),
#         ('text-purple-500', 'Purple'),
#         ('text-red-500', 'Red'),
#         ('text-gray-500', 'Gray'),
#     ]
#
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     duration = models.IntegerField()  # у хвилинах
#     questions = models.IntegerField(default=30)
#     icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='DiJsBadge')
#     color = models.CharField(max_length=50, choices=COLOR_CHOICES, default='text-gray-500')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     comments = GenericRelation('Comment', related_query_name='test')
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name = 'Тест'
#         verbose_name_plural = 'Тести'
#         ordering = ['id']
#
#
# class Question(models.Model):
#     test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='test_questions')
#     question = models.TextField()
#     # Видаляємо непотрібні поля
#     # code = models.TextField(null=True, blank=True)
#     # hint = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.test.title} - {self.question[:50]}..."
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         # Перевіряємо кількість правильних відповідей
#         correct_answers = self.answers.filter(is_correct=True)
#         # Якщо більше однієї правильної відповіді, залишаємо тільки першу
#         if correct_answers.count() > 1:
#             first_correct = correct_answers.first()
#             for answer in correct_answers.exclude(id=first_correct.id):
#                 answer.is_correct = False
#                 answer.save()
#
#     class Meta:
#         verbose_name = 'Питання для тестів'
#         verbose_name_plural = 'Питання для тестів'
#         ordering = ['created_at']
#
#
# class Answer(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
#     text = models.TextField()
#     is_correct = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f"{self.text[:50]}... ({'Правильно' if self.is_correct else 'Неправильно'})"
#
#     def save(self, *args, **kwargs):
#         # Переконуємося, що текст відповіді не порожній
#         if not self.text.strip():
#             return  # Не зберігаємо порожні відповіді
#
#         # Якщо це правильна відповідь, переконуємося, що інші відповіді неправильні
#         if self.is_correct:
#             self.question.answers.exclude(id=self.id).update(is_correct=False)
#
#         super().save(*args, **kwargs)
#
#         # Після збереження перевіряємо, чи є хоч одна правильна відповідь
#         if not self.question.answers.filter(is_correct=True).exists():
#             # Якщо немає правильних відповідей, встановлюємо першу як правильну
#             first_answer = self.question.answers.first()
#             if first_answer:
#                 first_answer.is_correct = True
#                 first_answer.save(update_fields=['is_correct'])
#
#     class Meta:
#         verbose_name = 'Відповідь'
#         verbose_name_plural = 'Відповіді'
#
#
# class UserProgress(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
#     test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='user_progress')
#     score = models.IntegerField()  # Зберігаємо як відсоток
#     attempts = models.IntegerField(default=0)  # Кількість спроб
#     completed_at = models.DateTimeField(auto_now=True)  # Змінено з auto_now_add на auto_now
#
#     def __str__(self):
#         return f"{self.user.username} - {self.test.title}: {self.score}% ({self.attempts} спроб)"
#
#     class Meta:
#         verbose_name = 'Прогрес тесту'
#         verbose_name_plural = 'Прогрес тестів'
#         ordering = ['-completed_at']
#         unique_together = ['user', 'test']  # Один запис прогресу на тест для користувача
#
#
# class TestAttempt(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_attempts')
#     test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='attempts')
#     score = models.IntegerField()  # Відсоток правильних відповідей
#     correct_answers = models.IntegerField()  # Кількість правильних відповідей
#     total_questions = models.IntegerField()  # Загальна кількість питань
#     completed_at = models.DateTimeField(auto_now_add=True)  # Час завершення тесту
#
#     # Зв'язок з UserProgress для зручного доступу, додаємо related_name щоб уникнути конфлікту
#     progress = models.ForeignKey(
#         UserProgress,
#         on_delete=models.CASCADE,
#         related_name='test_history',  # Змінено з 'attempts' на 'test_history'
#         null=True
#     )
#
#     def __str__(self):
#         return f"{self.user.username} - {self.test.title}: {self.score}% ({self.correct_answers}/{self.total_questions})"
#
#     def save(self, *args, **kwargs):
#         # Створюємо або оновлюємо основний прогрес користувача
#         progress, created = UserProgress.objects.get_or_create(
#             user=self.user,
#             test=self.test,
#             defaults={'score': self.score, 'attempts': 1}
#         )
#
#         if not created:
#             # Оновлюємо існуючий прогрес
#             progress.score = self.score  # Зберігаємо останній результат
#             progress.attempts += 1  # Збільшуємо кількість спроб
#             progress.save()
#
#         # Зберігаємо зв'язок з прогресом
#         self.progress = progress
#
#         super().save(*args, **kwargs)
#
#     class Meta:
#         verbose_name = 'Спроба тесту'
#         verbose_name_plural = 'Спроби тестів'
#         ordering = ['-completed_at']
#
#
# class InteractiveTask(models.Model):
#     TASK_TYPE_CHOICES = [
#         ('complete', 'Дописати код'),
#         ('fill_gap', 'Заповнити пропуск'),
#         ('fix_bug', 'Виправити помилку'),
#     ]
#
#     test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='interactive_tasks')
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     initial_code = models.TextField(help_text="Початковий код завдання")
#     task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='complete')
#     difficulty = models.IntegerField(default=1, help_text="Рівень складності від 1 до 5")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.test.title} - {self.title}"
#
#     def save(self, *args, **kwargs):
#         # Замінюємо literal переноси рядків на справжні для коректного відображення в редакторі
#         self.initial_code = self.initial_code.replace('\\n', '\n')
#         super().save(*args, **kwargs)
#
#     class Meta:
#         verbose_name = 'Інтерактивне завдання'
#         verbose_name_plural = 'Інтерактивні завдання'
#         ordering = ['test', 'difficulty', 'created_at']
#
#
# class TaskSolution(models.Model):
#     task = models.ForeignKey(InteractiveTask, on_delete=models.CASCADE, related_name='solutions')
#     solution_code = models.TextField(help_text="Правильний варіант рішення")
#     is_primary = models.BooleanField(default=False, help_text="Чи це основне рішення")
#     hint = models.TextField(blank=True, null=True, help_text="Підказка для цього рішення")
#
#     def __str__(self):
#         return f"Рішення для {self.task.title} ({'Основне' if self.is_primary else 'Альтернативне'})"
#
#     class Meta:
#         verbose_name = 'Рішення завдання'
#         verbose_name_plural = 'Рішення завдань'
#
#
# class TaskAttempt(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_attempts')
#     task = models.ForeignKey(InteractiveTask, on_delete=models.CASCADE, related_name='attempts')
#     submitted_code = models.TextField()
#     is_correct = models.BooleanField()
#     completed_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.user.username} - {self.task.title} - {'Успішно' if self.is_correct else 'Невдало'}"
#
#     class Meta:
#         verbose_name = 'Спроба інтерактивного завдання'
#         verbose_name_plural = 'Спроби інтерактивних завдань'
#         ordering = ['-completed_at']
#
#
# class UserTaskProgress(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_progress')
#     test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='user_task_progress')
#     completed_tasks = models.IntegerField(default=0)
#     total_tasks = models.IntegerField(default=0)
#     last_updated = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.user.username} - {self.test.title}: {self.completed_tasks}/{self.total_tasks}"
#
#     class Meta:
#         verbose_name = 'Прогрес інтерактивних завдань'
#         verbose_name_plural = 'Прогрес інтерактивних завдань'
#         unique_together = ['user', 'test']
#
#
# class Article(models.Model):
#     TYPE_CHOICES = (
#         ('news', 'Новина'),
#         ('task', 'Завдання'),
#     )
#
#     title = models.CharField(max_length=200, verbose_name="Заголовок")
#     slug = models.SlugField(max_length=250, unique=True, blank=True)
#     article_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='news', verbose_name="Тип статті")
#     description = models.TextField(
#         verbose_name="Короткий опис",
#         help_text="Короткий опис для списку статей. Підтримує HTML-теги. Використовуйте <strong>текст</strong> для виділення жирним.",
#         null=True,
#         blank=True
#     )
#     summary = models.TextField(
#         verbose_name="Підсумок",
#         help_text="Підсумковий текст наприкінці статті. Підтримує HTML-теги. Використовуйте <strong>текст</strong> для виділення жирним.",
#         blank=True
#     )
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles", verbose_name="Автор")
#     published_at = models.DateTimeField(verbose_name="Дата публікації")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
#     featured = models.BooleanField(default=False, verbose_name="Рекомендована стаття")
#     thumbnail = models.ImageField(upload_to='articles/thumbnails/', blank=True, null=True,
#                                   verbose_name="Головне зображення")
#     comments = GenericRelation('Comment', related_query_name='article')
#
#     class Meta:
#         ordering = ['-published_at']
#         verbose_name = "Стаття"
#         verbose_name_plural = "Статті"
#
#     def __str__(self):
#         return self.title
#
#     def save(self, *args, **kwargs):
#         # Auto-generate slug if not provided
#         if not self.slug:
#             self.slug = slugify(self.title)
#         # Set published_at to now if not set
#         if not self.published_at:
#             from django.utils import timezone
#             self.published_at = timezone.now()
#         super().save(*args, **kwargs)
#
#
# class ArticleSection(models.Model):
#     LANGUAGE_CHOICES = (
#         ('html', 'HTML'),
#         ('css', 'CSS'),
#         ('javascript', 'JavaScript'),
#         ('jsx', 'React'),
#         ('sql', 'SQL'),
#         ('python', 'Python'),
#     )
#
#     article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="sections", verbose_name="Стаття")
#     order = models.PositiveSmallIntegerField(default=0, verbose_name="Порядок відображення")
#     title = models.CharField(max_length=255, blank=True, verbose_name="Заголовок секції")
#
#     # Content fields - all optional
#     content = models.TextField(
#         blank=True,
#         verbose_name="Текстовий вміст",
#         help_text="Підтримує HTML-теги. Використовуйте <strong>текст</strong> для виділення жирним."
#     )
#     image = models.ImageField(upload_to='articles/images/', blank=True, null=True, verbose_name="Зображення")
#     image_caption = models.CharField(max_length=255, blank=True, verbose_name="Підпис до зображення")
#     code = models.TextField(blank=True, verbose_name="Код")
#     language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES, default='javascript',
#                               blank=True, verbose_name="Мова програмування")
#     code_description = models.TextField(blank=True, verbose_name="Опис коду")
#
#     class Meta:
#         ordering = ['order']
#         verbose_name = "Секція статті"
#         verbose_name_plural = "Секції статей"
#
#     def __str__(self):
#         return f"Секція для {self.article.title} (#{self.order})"
#
#
# class Comment(models.Model):
#     code = models.TextField(blank=True, null=True, verbose_name="Код")
#     code_language = models.CharField(max_length=20, blank=True, null=True, verbose_name="Мова коду")
#     has_code = models.BooleanField(default=False, verbose_name="Містить код")
#
#     content = models.TextField(verbose_name="Коментар")
#     author_name = models.CharField(max_length=100, verbose_name="Ім'я автора")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
#
#     # Optional relation to registered user (can be null for anonymous comments)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
#                              related_name="comments", verbose_name="Користувач")
#
#     # Parent comment (for replies) - self-reference
#     parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
#                                related_name="replies", verbose_name="Батьківський коментар")
#
#     # Content type references (using generic relations)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Тип контенту")
#     object_id = models.PositiveIntegerField(verbose_name="ID об'єкту")
#     content_object = GenericForeignKey('content_type', 'object_id')
#
#     data_processing_agreed = models.BooleanField(default=False, verbose_name="Згода на обробку даних")
#
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Коментар"
#         verbose_name_plural = "Коментарі"
#         indexes = [
#             models.Index(fields=['content_type', 'object_id']),
#         ]
#
#     def __str__(self):
#         return f"{self.author_name}: {self.content[:50]}..."
#
#
# class InterviewVideo(models.Model):
#     CATEGORY_CHOICES = [
#         ('frontend', 'Frontend'),
#         ('backend', 'Backend'),
#         ('fullstack', 'Full Stack'),
#         ('devops', 'DevOps'),
#         ('mobile', 'Mobile'),
#         ('qa', 'QA'),
#         ('other', 'Інше'),
#     ]
#
#     LEVEL_CHOICES = [
#         ('junior', 'Junior'),
#         ('middle', 'Middle'),
#         ('senior', 'Senior'),
#     ]
#
#     title = models.CharField(max_length=200, verbose_name="Заголовок")
#     youtube_id = models.CharField(max_length=20, verbose_name="ID відео на YouTube")
#     description = models.TextField(verbose_name="Опис")
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='frontend', verbose_name="Категорія")
#     level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='junior', verbose_name="Рівень")
#     featured = models.BooleanField(default=False, verbose_name="Рекомендоване")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата додавання")
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name = "Відео співбесіди"
#         verbose_name_plural = "Відео співбесід"
#         ordering = ['-featured', '-created_at']
#
#
# class ForumTopic(models.Model):
#     CATEGORY_CHOICES = [
#         ('technical', 'Технічні питання'),
#         ('interview', 'Питання до співбесід'),
#         ('career', 'Кар\'єра'),
#         ('other', 'Інше'),
#     ]
#
#     title = models.CharField(max_length=255, verbose_name="Заголовок теми")
#     content = models.TextField(verbose_name="Зміст теми")
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other', verbose_name="Категорія")
#     author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="forum_topics", verbose_name="Автор")
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
#     updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
#     views = models.PositiveIntegerField(default=0, verbose_name="Кількість переглядів")
#     is_pinned = models.BooleanField(default=False, verbose_name="Закріплена тема")
#
#     # Нові поля
#     likes = models.ManyToManyField(User, related_name="liked_topics", blank=True, verbose_name="Лайки")
#     bookmarks = models.ManyToManyField(User, related_name="bookmarked_topics", blank=True, verbose_name="Закладки")
#     has_code = models.BooleanField(default=False, verbose_name="Містить код")
#
#     # Використовуємо існуюче рішення для коментарів
#     comments = GenericRelation('Comment', related_query_name='forum_topic')
#
#     def __str__(self):
#         return self.title
#
#     class Meta:
#         verbose_name = "Тема форуму"
#         verbose_name_plural = "Теми форуму"
#         ordering = ['-is_pinned', '-created_at']

# core/models.py
from django.db import models

class TimestampedModel(models.Model):
    """Базова модель з часовими мітками для наслідування."""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        abstract = True