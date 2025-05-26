# core/admin.py

from django.contrib import admin
# from django.db import models
# from .models import Test, Question, Answer, UserProgress, InteractiveTask, TaskSolution, TaskAttempt, UserTaskProgress, \
#     Article, ArticleSection, Comment, InterviewVideo, ForumTopic
# from django.contrib.admin.widgets import AdminTextareaWidget
# from django.utils.html import format_html
# from django.contrib.contenttypes.models import ContentType
#
#
# class AnswerInline(admin.TabularInline):
#     model = Answer
#     extra = 4  # 4 поля для відповідей за замовчуванням
#     max_num = 4  # Максимум 4 відповіді
#     min_num = 4  # Мінімум 4 відповіді
#     validate_min = True
#
#     def formfield_for_dbfield(self, db_field, **kwargs):
#         formfield = super().formfield_for_dbfield(db_field, **kwargs)
#         if db_field.name == 'text':
#             formfield.widget.attrs.update({
#                 'required': 'required',
#                 'placeholder': 'Введіть варіант відповіді',
#             })
#         return formfield
#
#
# @admin.register(Question)
# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('test', 'question_preview', 'correct_answer', 'created_at')
#     list_filter = ('test',)
#     search_fields = ('question',)
#     inlines = [AnswerInline]
#
#     def question_preview(self, obj):
#         return obj.question[:50] + '...' if len(obj.question) > 50 else obj.question
#
#     def correct_answer(self, obj):
#         correct = obj.answers.filter(is_correct=True).first()
#         if correct:
#             return correct.text[:30] + '...' if len(correct.text) > 30 else correct.text
#         return "Немає правильної відповіді"
#
#     question_preview.short_description = 'Питання'
#     correct_answer.short_description = 'Правильна відповідь'
#
#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#
#         # Перевірка наявності хоча б однієї правильної відповіді
#         if not obj.answers.filter(is_correct=True).exists():
#             first_answer = obj.answers.first()
#             if first_answer:
#                 first_answer.is_correct = True
#                 first_answer.save()
#                 self.message_user(request, 'Автоматично встановлено першу відповідь як правильну.')
#
#     def save_formset(self, request, form, formset, change):
#         instances = formset.save(commit=False)
#
#         # Лічильник правильних відповідей
#         correct_count = 0
#
#         # Перевіряємо, скільки правильних відповідей
#         for instance in instances:
#             if hasattr(instance, 'is_correct') and instance.is_correct:
#                 correct_count += 1
#
#         # Якщо більше однієї правильної відповіді, показуємо повідомлення
#         if correct_count > 1:
#             self.message_user(request, 'Увага: Буде збережена тільки одна правильна відповідь!', level='WARNING')
#
#         # Якщо немає правильних відповідей, встановлюємо першу як правильну
#         if correct_count == 0 and instances:
#             instances[0].is_correct = True
#             self.message_user(request,
#                               'Автоматично встановлено першу відповідь як правильну, оскільки не вказано правильної відповіді.')
#
#         # Зберігаємо всі відповіді
#         for instance in instances:
#             # Перевіряємо, чи не порожня відповідь
#             if hasattr(instance, 'text') and instance.text.strip():
#                 instance.save()
#
#         # Видаляємо відзначені для видалення
#         formset.save_m2m()
#
#
# @admin.register(Test)
# class TestAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'questions', 'description','duration', 'created_at')
#     list_filter = ('created_at',)
#     search_fields = ('title', 'description')
#     ordering = ('id',)
#     list_editable = ('questions', 'duration', 'description')
#
#
# @admin.register(UserProgress)
# class UserProgressAdmin(admin.ModelAdmin):
#     list_display = ('user', 'test', 'score', 'completed_at')
#     list_filter = ('test', 'completed_at')
#     search_fields = ('user__username', 'test__title')
#     raw_id_fields = ('user', 'test')
#
#
# class TaskSolutionInline(admin.TabularInline):
#     model = TaskSolution
#     extra = 1
#     min_num = 1
#     max_num = 5
#
#
# @admin.register(InteractiveTask)
# class InteractiveTaskAdmin(admin.ModelAdmin):
#     list_display = ('title', 'test', 'task_type', 'difficulty', 'created_at')
#     list_filter = ('test', 'task_type', 'difficulty')
#     search_fields = ('title', 'description', 'initial_code')
#     inlines = [TaskSolutionInline]
#
#     fieldsets = (
#         (None, {
#             'fields': ('test', 'title', 'description')
#         }),
#         ('Код', {
#             'fields': ('initial_code', 'task_type')
#         }),
#         ('Додатково', {
#             'fields': ('difficulty',)
#         }),
#     )
#
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         form.base_fields['initial_code'].widget.attrs['style'] = 'font-family: monospace; width: 100%; height: 300px;'
#         return form
#
#
# # @admin.register(TaskSolution)
# # class TaskSolutionAdmin(admin.ModelAdmin):
# #     list_display = ('task', 'is_primary')
# #     list_filter = ('is_primary', 'task__test')
# #     search_fields = ('solution_code', 'hint')
# #
# #     def get_form(self, request, obj=None, **kwargs):
# #         form = super().get_form(request, obj, **kwargs)
# #         form.base_fields['solution_code'].widget.attrs['style'] = 'font-family: monospace; width: 100%; height: 300px;'
# #         return form
#
#
# @admin.register(TaskAttempt)
# class TaskAttemptAdmin(admin.ModelAdmin):
#     list_display = ('user', 'task', 'is_correct', 'completed_at')
#     list_filter = ('is_correct', 'task__test', 'user')
#     search_fields = ('user__username', 'task__title', 'submitted_code')
#     readonly_fields = ('user', 'task', 'submitted_code', 'is_correct', 'completed_at')
#
#
# @admin.register(UserTaskProgress)
# class UserTaskProgressAdmin(admin.ModelAdmin):
#     list_display = ('user', 'test', 'completed_tasks', 'total_tasks', 'last_updated')
#     list_filter = ('test',)
#     search_fields = ('user__username', 'test__title')
#
#
# # class ArticleImageInline(admin.TabularInline):
# #     model = ArticleImage
# #     extra = 1
# #     fields = ('image', 'caption', 'position', 'order')
# #
# #
# # class ArticleCodeSnippetInline(admin.TabularInline):
# #     model = ArticleCodeSnippet
# #     extra = 1
# #     fields = ('language', 'title', 'code', 'description', 'position', 'order')
# #
# #
# # @admin.register(Article)
# # class ArticleAdmin(admin.ModelAdmin):
# #     list_display = ('title', 'author', 'published_at', 'updated_at', 'featured')
# #     list_filter = ('featured', 'published_at')
# #     search_fields = ('title', 'content', 'summary')
# #     prepopulated_fields = {'slug': ('title',)}
# #     inlines = [ArticleImageInline, ArticleCodeSnippetInline]
# #     date_hierarchy = 'published_at'
# #
# #     def save_model(self, request, obj, form, change):
# #         # Auto-set the author if not specified
# #         if not obj.author_id:
# #             obj.author = request.user
# #         super().save_model(request, obj, form, change)
# #
# #
# # @admin.register(ArticleImage)
# # class ArticleImageAdmin(admin.ModelAdmin):
# #     list_display = ('article', 'caption', 'position', 'order')
# #     list_filter = ('position', 'article')
# #     search_fields = ('caption', 'article__title')
# #
# #
# # @admin.register(ArticleCodeSnippet)
# # class ArticleCodeSnippetAdmin(admin.ModelAdmin):
# #     list_display = ('article', 'language', 'title', 'position', 'order')
# #     list_filter = ('language', 'position', 'article')
# #     search_fields = ('title', 'code', 'article__title')
#
#
# # from django.contrib import admin
# # from django.db import models
# # from django.contrib.admin.widgets import AdminTextareaWidget
# # from django.utils.html import format_html
#
#
# # Create a custom widget for HTML fields with larger size
# class CustomTextareaWidget(AdminTextareaWidget):
#     def __init__(self, attrs=None):
#         default_attrs = {'rows': '12', 'cols': '80', 'style': 'font-family: monospace; line-height: 1.5;'}
#         if attrs:
#             default_attrs.update(attrs)
#         super().__init__(default_attrs)
#
#
# class ArticleSectionInline(admin.StackedInline):
#     model = ArticleSection
#     extra = 0
#     classes = ('collapse-open',)
#
#     fieldsets = (
#         (None, {
#             'fields': ('order', 'title'),
#         }),
#         ('Вміст секції', {
#             'fields': ('content', 'image', 'image_caption', 'code', 'language', 'code_description'),
#             'classes': ('collapse-open',),
#             'description': format_html(
#                 'Кожна секція може містити будь-яку комбінацію тексту, зображення та коду.<br><br>'
#                 '<strong style="background-color: #f8f8f8; padding: 3px 6px; border: 1px solid #ddd; border-radius: 3px;">HTML-форматування:</strong><br>'
#                 '- Жирний текст: &lt;strong&gt;текст&lt;/strong&gt;<br>'
#                 '- Курсив: &lt;em&gt;текст&lt;/em&gt;<br>'
#                 '- Перенос рядка: &lt;br&gt;'
#             ),
#         }),
#     )
#
#     formfield_overrides = {
#         models.TextField: {'widget': CustomTextareaWidget},
#     }
#
#
# @admin.register(Article)
# class ArticleAdmin(admin.ModelAdmin):
#     list_display = ('title', 'article_type', 'author', 'published_at', 'updated_at', 'featured')
#     list_filter = ('article_type', 'featured', 'published_at')
#     search_fields = ('title', 'description', 'summary')
#     prepopulated_fields = {'slug': ('title',)}
#     inlines = [ArticleSectionInline]
#     date_hierarchy = 'published_at'
#
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'slug', 'article_type', 'author')
#         }),
#         ('Контент', {
#             'fields': ('thumbnail', 'description', 'summary'),
#             'classes': ('collapse-open',),
#             'description': format_html(
#                 'Підтримується HTML-форматування.<br><br>'
#                 '<strong style="background-color: #f8f8f8; padding: 3px 6px; border: 1px solid #ddd; border-radius: 3px;">Приклади форматування:</strong><br>'
#                 '- Жирний текст: &lt;strong&gt;текст&lt;/strong&gt;<br>'
#                 '- Курсив: &lt;em&gt;текст&lt;/em&gt;<br>'
#                 '- Перенос рядка: &lt;br&gt;'
#             ),
#         }),
#         ('Налаштування', {
#             'fields': ('published_at', 'featured'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     formfield_overrides = {
#         models.TextField: {'widget': CustomTextareaWidget},
#     }
#
#     def save_model(self, request, obj, form, change):
#         # Auto-set the author if not specified
#         if not obj.author_id:
#             obj.author = request.user
#         super().save_model(request, obj, form, change)
#
#
# # @admin.register(ArticleSection)
# # class ArticleSectionAdmin(admin.ModelAdmin):
# #     list_display = ('article', 'title', 'order', 'has_content', 'has_image', 'has_code')
# #     list_filter = ('article',)
# #     search_fields = ('title', 'content', 'code', 'article__title')
# #
# #     fieldsets = (
# #         (None, {
# #             'fields': ('article', 'order', 'title')
# #         }),
# #         ('Вміст секції', {
# #             'fields': ('content', 'image', 'image_caption', 'code', 'language', 'code_description'),
# #             'classes': ('collapse-open',),
# #             'description': format_html(
# #                 'Кожна секція може містити будь-яку комбінацію тексту, зображення та коду.<br><br>'
# #                 '<strong style="background-color: #f8f8f8; padding: 3px 6px; border: 1px solid #ddd; border-radius: 3px;">HTML-форматування:</strong><br>'
# #                 '- Жирний текст: &lt;strong&gt;текст&lt;/strong&gt;<br>'
# #                 '- Курсив: &lt;em&gt;текст&lt;/em&gt;<br>'
# #                 '- Перенос рядка: &lt;br&gt;'
# #             ),
# #         }),
# #     )
# #
# #     formfield_overrides = {
# #         models.TextField: {'widget': CustomTextareaWidget},
# #     }
# #
# #     def has_content(self, obj):
# #         return bool(obj.content)
# #
# #     has_content.short_description = 'Має текст'
# #     has_content.boolean = True
# #
# #     def has_image(self, obj):
# #         return bool(obj.image)
# #
# #     has_image.short_description = 'Має зображення'
# #     has_image.boolean = True
# #
# #     def has_code(self, obj):
# #         return bool(obj.code)
# #
# #     has_code.short_description = 'Має код'
# #     has_code.boolean = True
#
# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = (
#     'author_display', 'short_content', 'content_object_display', 'has_parent', 'data_processing_agreed', 'created_at')
#     list_filter = ('created_at', 'data_processing_agreed', 'content_type')
#     search_fields = ('content', 'author_name', 'user__username')
#     readonly_fields = ('created_at', 'content_type', 'object_id', 'content_object_display', 'user')
#     raw_id_fields = ('parent',)
#
#     formfield_overrides = {
#         models.TextField: {'widget': CustomTextareaWidget},
#     }
#
#     fieldsets = (
#         (None, {
#             'fields': ('content', 'author_name', 'user')
#         }),
#         ('Зв\'язки', {
#             'fields': ('parent', 'content_type', 'object_id', 'content_object_display'),
#             'classes': ('collapse-open',),
#         }),
#         ('Налаштування', {
#             'fields': ('created_at', 'data_processing_agreed'),
#             'classes': ('collapse',),
#         }),
#     )
#
#     def short_content(self, obj):
#         if len(obj.content) > 80:
#             return obj.content[:77] + '...'
#         return obj.content
#
#     short_content.short_description = 'Коментар'
#
#     def author_display(self, obj):
#         if obj.user:
#             return format_html('<strong>{}</strong> ({})', obj.author_name, obj.user.username)
#         return obj.author_name
#
#     author_display.short_description = 'Автор'
#
#     def content_object_display(self, obj):
#         if obj.content_type and obj.object_id:
#             content_type = obj.content_type
#             model_class = content_type.model_class()
#             try:
#                 instance = model_class.objects.get(id=obj.object_id)
#                 if hasattr(instance, 'title'):
#                     return format_html('{}: <a href="/admin/{}/{}/{}/change/">{}</a>',
#                                        content_type.name,
#                                        content_type.app_label,
#                                        content_type.model,
#                                        obj.object_id,
#                                        instance.title)
#                 return format_html('{}: <a href="/admin/{}/{}/{}/change/">ID: {}</a>',
#                                    content_type.name,
#                                    content_type.app_label,
#                                    content_type.model,
#                                    obj.object_id,
#                                    obj.object_id)
#             except model_class.DoesNotExist:
#                 return f"{content_type.name}: (видалено, ID:{obj.object_id})"
#         return '-'
#
#     content_object_display.short_description = 'Прикріплено до'
#
#     def has_parent(self, obj):
#         return bool(obj.parent)
#
#     has_parent.boolean = True
#     has_parent.short_description = 'Відповідь'
#
# # core/admin.py (додати)
#
# @admin.register(InterviewVideo)
# class InterviewVideoAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'level', 'featured', 'created_at')
#     list_filter = ('category', 'level', 'featured')
#     search_fields = ('title', 'description')
#     readonly_fields = ('created_at',)
#
#
# @admin.register(ForumTopic)
# class ForumTopicAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'author', 'created_at', 'views', 'is_pinned', 'comments_count')
#     list_filter = ('category', 'is_pinned', 'created_at', 'has_code')
#     search_fields = ('title', 'content', 'author__username')
#     date_hierarchy = 'created_at'
#     readonly_fields = ('views', 'comments_count', 'created_at', 'updated_at')
#     actions = ['pin_topics', 'unpin_topics']
#
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'content', 'category', 'author', 'is_pinned', 'has_code')
#         }),
#         ('Статистика', {
#             'fields': ('views', 'comments_count', 'created_at', 'updated_at'),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def comments_count(self, obj):
#         return obj.comments.count()
#
#     comments_count.short_description = 'Коментарі'
#
#     def pin_topics(self, request, queryset):
#         queryset.update(is_pinned=True)
#         self.message_user(request, f"{queryset.count()} тем було закріплено")
#
#     pin_topics.short_description = "Закріпити вибрані теми"
#
#     def unpin_topics(self, request, queryset):
#         queryset.update(is_pinned=False)
#         self.message_user(request, f"{queryset.count()} тем було відкріплено")
#
#     unpin_topics.short_description = "Відкріпити вибрані теми"
#
#     def save_model(self, request, obj, form, change):
#         # Автоматично визначаємо наявність кодових вставок
#         if "```" in obj.content:
#             obj.has_code = True
#         super().save_model(request, obj, form, change)