from rest_framework import serializers
from tests.models import Test, Question, Answer, UserProgress, TestAttempt

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'title', 'icon', 'color', 'questions', 'duration', 'description']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question', 'answers']


class TestDetailSerializer(serializers.ModelSerializer):
    test_questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'title', 'icon', 'color', 'questions', 'duration', 'description', 'test_questions']


class TestAttemptSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    completed_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = TestAttempt
        fields = (
            'id',
            'test_title',
            'score',
            'correct_answers',
            'total_questions',
            'completed_at'
        )
        read_only_fields = ('completed_at',)


class UserProgressSerializer(serializers.ModelSerializer):
    test_title = serializers.CharField(source='test.title', read_only=True)
    test_id = serializers.IntegerField(source='test.id', read_only=True)
    completed_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    last_attempts = serializers.SerializerMethodField()

    class Meta:
        model = UserProgress
        fields = (
            'id',
            'test_id',
            'test_title',
            'score',
            'attempts',
            'completed_at',
            'last_attempts'
        )
        read_only_fields = ('completed_at', 'attempts')

    def get_last_attempts(self, obj):
        attempts = obj.test_history.all().order_by('-completed_at')[:5]
        return TestAttemptSerializer(attempts, many=True).data