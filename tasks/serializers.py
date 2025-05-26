from rest_framework import serializers
from tasks.models import InteractiveTask, TaskSolution, TaskAttempt, UserTaskProgress
from django.utils import timezone
from django.conf import settings
import pytz

class LocalDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if value is None:
            return None

        if timezone.is_aware(value):
            local_timezone = pytz.timezone(settings.TIME_ZONE)
            value = value.astimezone(local_timezone)

        return value.strftime("%d.%m.%Y %H:%M")

class TaskSolutionSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='solution_code', read_only=True)

    class Meta:
        model = TaskSolution
        fields = ['id', 'solution_code', 'code', 'is_primary', 'hint']
        read_only_fields = ['id']


class InteractiveTaskSerializer(serializers.ModelSerializer):
    solutions = TaskSolutionSerializer(many=True, read_only=True)
    test_title = serializers.CharField(source='test.title', read_only=True)

    class Meta:
        model = InteractiveTask
        fields = ['id', 'test', 'test_title', 'title', 'description', 'initial_code',
                  'task_type', 'difficulty', 'solutions']
        read_only_fields = ['id', 'test_title']

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'initial_code' in representation:
            representation['initial_code'] = instance.initial_code
        return representation


class InteractiveTaskDetailSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    solution = serializers.SerializerMethodField()
    solutions = TaskSolutionSerializer(many=True, read_only=True)

    class Meta:
        model = InteractiveTask
        fields = ['id', 'test', 'test_title', 'title', 'description', 'initial_code',
                  'task_type', 'difficulty', 'solution', 'solutions']
        read_only_fields = ['id', 'test_title']

    def get_solution(self, obj):
        try:
            primary_solution = obj.solutions.filter(is_primary=True).first()
            if primary_solution:
                return {
                    'solution_code': primary_solution.solution_code,
                    'code': primary_solution.solution_code,
                    'hint': primary_solution.hint
                }

            first_solution = obj.solutions.first()
            if first_solution:
                return {
                    'solution_code': first_solution.solution_code,
                    'code': first_solution.solution_code,
                    'hint': first_solution.hint
                }
        except Exception as e:
            print(f"Error getting solution: {str(e)}")
            return None

        return None


class TaskAttemptSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    test_title = serializers.CharField(source='task.test.title', read_only=True)
    completed_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = TaskAttempt
        fields = ['id', 'task', 'task_title', 'test_title', 'submitted_code', 'is_correct', 'completed_at']
        read_only_fields = ['id', 'task_title', 'test_title', 'completed_at']


class SubmitTaskSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    code = serializers.CharField()
    language = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate_task_id(self, value):
        try:
            InteractiveTask.objects.get(id=value)
        except InteractiveTask.DoesNotExist:
            raise serializers.ValidationError("Завдання не знайдено")
        return value


class UserTaskProgressSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    last_attempts = serializers.SerializerMethodField()
    last_updated = LocalDateTimeField(read_only=True)

    class Meta:
        model = UserTaskProgress
        fields = ['id', 'test', 'test_title', 'completed_tasks', 'total_tasks',
                  'completion_percentage', 'last_updated', 'last_attempts']
        read_only_fields = ['id', 'test_title', 'last_updated']

    def get_completion_percentage(self, obj):
        if obj.total_tasks == 0:
            return 0
        return round((obj.completed_tasks / obj.total_tasks) * 100)

    def get_last_attempts(self, obj):
        attempts = TaskAttempt.objects.filter(
            user=obj.user,
            task__test_id=obj.test.id
        ).order_by('-completed_at')[:5]
        return TaskAttemptSerializer(attempts, many=True).data