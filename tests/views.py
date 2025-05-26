from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Test, Question, UserProgress, TestAttempt
from .serializers import TestSerializer, TestDetailSerializer, UserProgressSerializer, TestAttemptSerializer


class TestListView(generics.ListAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = (permissions.AllowAny,)


class TestDetailView(generics.RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestDetailSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        test = self.get_object()

        questions = Question.objects.filter(test=test).order_by('?')[:test.questions]

        formatted_questions = []
        for idx, q in enumerate(questions):
            answers = list(q.answers.filter(text__isnull=False).exclude(text__exact=''))

            if len(answers) != 4:
                print(f"Warning: Question {q.id} has {len(answers)} answers, expected 4. Skipping.")
                continue

            correct_answers = [a for a in answers if a.is_correct]

            if len(correct_answers) != 1:
                if len(correct_answers) == 0 and answers:
                    answers[0].is_correct = True
                    answers[0].save()
                    correct_answer_idx = 0
                    print(f"Warning: Question {q.id} had no correct answer, set first as correct")
                elif len(correct_answers) > 1:
                    for a in correct_answers[1:]:
                        a.is_correct = False
                        a.save()
                    correct_answer_idx = answers.index(correct_answers[0])
                    print(f"Warning: Question {q.id} had multiple correct answers, keeping only first")
            else:
                correct_answer_idx = answers.index(correct_answers[0])

            formatted_answers = [a.text for a in answers]

            formatted_questions.append({
                'id': idx,
                'question': q.question,
                'answers': formatted_answers,
                'correctAnswerId': correct_answer_idx
            })

        response_data = {
            'id': test.id,
            'title': test.title,
            'icon': test.icon,
            'color': test.color,
            'questions': formatted_questions,
            'duration': test.duration,
            'description': test.description,
        }

        return Response(response_data)


class UserProgressListCreateView(generics.ListCreateAPIView):
    serializer_class = UserProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user).select_related('test')

    def create(self, request, *args, **kwargs):
        test_id = request.data.get('test_id')
        score = request.data.get('score')
        correct_answers = request.data.get('correct_answers')
        total_questions = request.data.get('total_questions')

        try:
            test = Test.objects.get(id=test_id)

            test_attempt = TestAttempt.objects.create(
                user=request.user,
                test=test,
                score=score,
                correct_answers=correct_answers,
                total_questions=total_questions
            )

            progress = UserProgress.objects.get(user=request.user, test=test)
            serializer = self.get_serializer(progress)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Test.DoesNotExist:
            return Response(
                {'error': 'Test not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TestAttemptListView(generics.ListAPIView):
    serializer_class = TestAttemptSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        test_id = self.kwargs.get('test_id')
        return TestAttempt.objects.filter(
            user=self.request.user,
            test_id=test_id
        ).order_by('-completed_at')


class UserProgressDetailView(generics.RetrieveAPIView):
    serializer_class = UserProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        test_id = self.kwargs.get('test_id')
        return get_object_or_404(
            UserProgress,
            user=self.request.user,
            test_id=test_id
        )