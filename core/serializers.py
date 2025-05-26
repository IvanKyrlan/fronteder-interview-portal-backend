# # core/serializers.py
# from django.contrib.contenttypes.models import ContentType
# from rest_framework import serializers
# from django.contrib.auth.models import User
# from .models import Test, UserProgress, TestAttempt, Answer, Question, InteractiveTask, TaskSolution, TaskAttempt, \
#     UserTaskProgress, Article, ArticleSection, Comment, InterviewVideo, ForumTopic
# from django.contrib.auth.password_validation import validate_password
# from django.utils import timezone
# from django.conf import settings
# import pytz
#
#
# class LocalDateTimeField(serializers.DateTimeField):
#     def to_representation(self, value):
#         if value is None:
#             return None
#
#         # Convert to the timezone defined in settings
#         if timezone.is_aware(value):
#             local_timezone = pytz.timezone(settings.TIME_ZONE)
#             value = value.astimezone(local_timezone)
#
#         # Format using the specified format
#         return value.strftime("%d.%m.%Y %H:%M")
#
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('id', 'username', 'email', 'first_name', 'last_name')
#         read_only_fields = ('id',)
#
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password_confirm = serializers.CharField(write_only=True, required=True)
#     email = serializers.EmailField(required=True)
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password', 'password_confirm')
#
#     def validate_username(self, value):
#         if User.objects.filter(username=value).exists():
#             raise serializers.ValidationError("Користувач з таким ім'ям вже існує")
#         return value
#
#     def validate_email(self, value):
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("Користувач з таким email вже існує")
#         return value
#
#     def validate(self, data):
#         if data['password'] != data['password_confirm']:
#             raise serializers.ValidationError({"password": "Паролі не співпадають"})
#         return data
#
#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user
#
# class ChangePasswordSerializer(serializers.Serializer):
#     current_password = serializers.CharField(required=True)
#     new_password = serializers.CharField(required=True, validators=[validate_password])
#
#     def validate_current_password(self, value):
#         user = self.context['request'].user
#         if not user.check_password(value):
#             raise serializers.ValidationError("Невірний поточний пароль")
#         return value
#
# class TestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Test
#         fields = ['id', 'title', 'icon', 'color', 'questions', 'duration', 'description']
#
#
# class AnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Answer
#         fields = ['id', 'text', 'is_correct']
#
#
# class QuestionSerializer(serializers.ModelSerializer):
#     answers = AnswerSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Question
#         fields = ['id', 'question', 'code', 'hint', 'answers']
#
#
# class TestDetailSerializer(serializers.ModelSerializer):
#     test_questions = QuestionSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Test
#         fields = ['id', 'title', 'icon', 'color', 'questions', 'duration', 'description', 'test_questions']
#
# # Update the TestAttemptSerializer
# class TestAttemptSerializer(serializers.ModelSerializer):
#     test_title = serializers.CharField(source='test.title', read_only=True)
#     # The format will be applied automatically from the REST_FRAMEWORK settings
#     completed_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
#
#     class Meta:
#         model = TestAttempt
#         fields = (
#             'id',
#             'test_title',
#             'score',
#             'correct_answers',
#             'total_questions',
#             'completed_at'
#         )
#         read_only_fields = ('completed_at',)
#
#
# class UserProgressSerializer(serializers.ModelSerializer):
#     test_title = serializers.CharField(source='test.title', read_only=True)
#     test_id = serializers.IntegerField(source='test.id', read_only=True)
#     # The format will be applied automatically
#     completed_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
#     last_attempts = serializers.SerializerMethodField()
#
#     class Meta:
#         model = UserProgress
#         fields = (
#             'id',
#             'test_id',
#             'test_title',
#             'score',
#             'attempts',
#             'completed_at',
#             'last_attempts'
#         )
#         read_only_fields = ('completed_at', 'attempts')
#
#     def get_last_attempts(self, obj):
#         attempts = obj.test_history.all().order_by('-completed_at')[:5]
#         return TestAttemptSerializer(attempts, many=True).data
#
#
# class TaskSolutionSerializer(serializers.ModelSerializer):
#     """Simple serializer for task solutions"""
#     # Add code field to match frontend expectations
#     code = serializers.CharField(source='solution_code', read_only=True)
#
#     class Meta:
#         model = TaskSolution
#         fields = ['id', 'solution_code', 'code', 'is_primary', 'hint']
#         read_only_fields = ['id']
#
#
# class InteractiveTaskSerializer(serializers.ModelSerializer):
#     solutions = TaskSolutionSerializer(many=True, read_only=True)
#     test_title = serializers.CharField(source='test.title', read_only=True)
#
#     class Meta:
#         model = InteractiveTask
#         fields = ['id', 'test', 'test_title', 'title', 'description', 'initial_code',
#                   'task_type', 'difficulty', 'solutions']
#         read_only_fields = ['id', 'test_title']
#
#     def to_representation(self, instance):
#         representation = super().to_representation(instance)
#         # Переконуємося, що initial_code правильно відображає переноси рядків
#         if 'initial_code' in representation:
#             representation['initial_code'] = instance.initial_code
#         return representation
#
#
# class InteractiveTaskDetailSerializer(serializers.ModelSerializer):
#     """Serializer for task details with solutions"""
#     test_title = serializers.CharField(source='test.title', read_only=True)
#     # Include both a single primary solution and all solutions
#     solution = serializers.SerializerMethodField()
#     # Don't specify source='solutions' as it's already the default related name
#     solutions = TaskSolutionSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = InteractiveTask
#         fields = ['id', 'test', 'test_title', 'title', 'description', 'initial_code',
#                   'task_type', 'difficulty', 'solution', 'solutions']
#         read_only_fields = ['id', 'test_title']
#
#     def get_solution(self, obj):
#         """Get primary solution or first available solution"""
#         try:
#             # Get primary solution first
#             primary_solution = obj.solutions.filter(is_primary=True).first()
#             if primary_solution:
#                 return {
#                     'solution_code': primary_solution.solution_code,
#                     'code': primary_solution.solution_code,
#                     'hint': primary_solution.hint
#                 }
#
#             # Fallback to first solution
#             first_solution = obj.solutions.first()
#             if first_solution:
#                 return {
#                     'solution_code': first_solution.solution_code,
#                     'code': first_solution.solution_code,
#                     'hint': first_solution.hint
#                 }
#         except Exception as e:
#             print(f"Error getting solution: {str(e)}")
#             return None
#
#         return None
#
#
# class TaskAttemptSerializer(serializers.ModelSerializer):
#     task_title = serializers.CharField(source='task.title', read_only=True)
#     test_title = serializers.CharField(source='task.test.title', read_only=True)
#     # The format will be applied automatically
#     completed_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
#
#     class Meta:
#         model = TaskAttempt
#         fields = ['id', 'task', 'task_title', 'test_title', 'submitted_code', 'is_correct', 'completed_at']
#         read_only_fields = ['id', 'task_title', 'test_title', 'completed_at']
#
#
# class SubmitTaskSerializer(serializers.Serializer):
#     task_id = serializers.IntegerField()
#     code = serializers.CharField()
#     language = serializers.CharField(required=False, allow_null=True, allow_blank=True)
#
#     def validate_task_id(self, value):
#         try:
#             InteractiveTask.objects.get(id=value)
#         except InteractiveTask.DoesNotExist:
#             raise serializers.ValidationError("Завдання не знайдено")
#         return value
#
#
# class UserTaskProgressSerializer(serializers.ModelSerializer):
#     test_title = serializers.CharField(source='test.title', read_only=True)
#     completion_percentage = serializers.SerializerMethodField()
#     last_attempts = serializers.SerializerMethodField()
#     # Use the custom field for date formatting
#     last_updated = LocalDateTimeField(read_only=True)
#
#     class Meta:
#         model = UserTaskProgress
#         fields = ['id', 'test', 'test_title', 'completed_tasks', 'total_tasks',
#                   'completion_percentage', 'last_updated', 'last_attempts']
#         read_only_fields = ['id', 'test_title', 'last_updated']
#
#     def get_completion_percentage(self, obj):
#         if obj.total_tasks == 0:
#             return 0
#         return round((obj.completed_tasks / obj.total_tasks) * 100)
#
#     def get_last_attempts(self, obj):
#         attempts = TaskAttempt.objects.filter(
#             user=obj.user,
#             task__test_id=obj.test.id
#         ).order_by('-completed_at')[:5]
#         return TaskAttemptSerializer(attempts, many=True).data
#
# class ArticleSectionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ArticleSection
#         fields = [
#             'id', 'order', 'title',
#             'content', 'image', 'image_caption',
#             'code', 'language', 'code_description'
#         ]
#
# class ArticleListSerializer(serializers.ModelSerializer):
#     author_name = serializers.CharField(source='author.username', read_only=True)
#     article_type_display = serializers.CharField(source='get_article_type_display', read_only=True)
#     published_at = LocalDateTimeField(read_only=True)
#
#     class Meta:
#         model = Article
#         fields = [
#             'id', 'title', 'slug', 'description', 'thumbnail',
#             'author_name', 'published_at', 'article_type', 'article_type_display'
#         ]
#
# class ArticleDetailSerializer(serializers.ModelSerializer):
#     author_name = serializers.CharField(source='author.username', read_only=True)
#     sections = ArticleSectionSerializer(many=True, read_only=True)
#     article_type_display = serializers.CharField(source='get_article_type_display', read_only=True)
#     published_at = LocalDateTimeField(read_only=True)
#
#     class Meta:
#         model = Article
#         fields = [
#             'id', 'title', 'slug', 'description', 'summary',
#             'thumbnail', 'author_name', 'published_at',
#             'article_type', 'article_type_display', 'sections'
#         ]
#
#
# class CommentUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username']
#
#
# class RecursiveCommentSerializer(serializers.Serializer):
#     def to_representation(self, instance):
#         serializer = self.parent.parent.__class__(instance, context=self.context)
#         return serializer.data
#
#
# class CommentSerializer(serializers.ModelSerializer):
#     user = CommentUserSerializer(read_only=True)
#     replies = RecursiveCommentSerializer(many=True, read_only=True)
#     created_at = LocalDateTimeField(read_only=True)
#
#     class Meta:
#         model = Comment
#         fields = [
#             'id', 'content', 'author_name', 'created_at',
#             'user', 'parent', 'replies', 'data_processing_agreed'
#         ]
#         read_only_fields = ['created_at', 'user']
#
#
# class CommentCreateSerializer(serializers.ModelSerializer):
#     content_type = serializers.CharField(write_only=True)
#     object_id = serializers.IntegerField(write_only=True)
#
#     class Meta:
#         model = Comment
#         fields = [
#             'content', 'author_name', 'parent',
#             'content_type', 'object_id', 'data_processing_agreed'
#         ]
#
#     def validate(self, data):
#         # Check if content_type is valid
#         content_type_str = data.pop('content_type')
#         try:
#             app_label, model = content_type_str.split('.')
#             data['content_type'] = ContentType.objects.get(app_label=app_label, model=model)
#         except (ValueError, ContentType.DoesNotExist):
#             raise serializers.ValidationError({'content_type': 'Invalid content type format or not found'})
#
#         # Validate data processing consent
#         if not data.get('data_processing_agreed'):
#             raise serializers.ValidationError({'data_processing_agreed': 'Необхідно погодитись на обробку даних'})
#
#         return data
#
#     def create(self, validated_data):
#         # If user is authenticated, associate comment with user
#         request = self.context.get('request')
#         if request and request.user.is_authenticated:
#             validated_data['user'] = request.user
#
#         return Comment.objects.create(**validated_data)
#
# class InterviewVideoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = InterviewVideo
#         fields = ['id', 'title', 'youtube_id', 'description', 'category', 'level', 'featured', 'created_at']
#
#
# class ForumTopicSerializer(serializers.ModelSerializer):
#     author_name = serializers.CharField(source='author.username', read_only=True)
#     comments_count = serializers.SerializerMethodField()
#     category_display = serializers.CharField(source='get_category_display', read_only=True)
#     created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
#
#     class Meta:
#         model = ForumTopic
#         fields = [
#             'id', 'title', 'content', 'category', 'category_display',
#             'author', 'author_name', 'created_at', 'updated_at',
#             'views', 'is_pinned', 'comments_count', 'has_code'
#         ]
#         read_only_fields = ['views', 'is_pinned', 'author_name', 'comments_count', 'author']
#
#     def get_comments_count(self, obj):
#         return obj.comments.count()