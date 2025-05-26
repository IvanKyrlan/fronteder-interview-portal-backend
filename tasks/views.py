from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
import re
import tempfile
import subprocess
import os

from .models import InteractiveTask, TaskSolution, TaskAttempt, UserTaskProgress
from tests.models import Test
from .serializers import (
    InteractiveTaskSerializer,
    InteractiveTaskDetailSerializer,
    TaskAttemptSerializer,
    SubmitTaskSerializer,
    UserTaskProgressSerializer,
)


class InteractiveTaskListView(generics.ListAPIView):
    serializer_class = InteractiveTaskDetailSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        test_id = self.kwargs.get('test_id')
        return InteractiveTask.objects.filter(test_id=test_id)


class InteractiveTaskDetailView(generics.RetrieveAPIView):
    queryset = InteractiveTask.objects.all()
    serializer_class = InteractiveTaskDetailSerializer
    permission_classes = (permissions.AllowAny,)


class SubmitTaskView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        serializer = SubmitTaskSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task_id = serializer.validated_data['task_id']
        submitted_code = serializer.validated_data['code']
        language = serializer.validated_data.get('language', None)

        task = get_object_or_404(InteractiveTask, id=task_id)

        solutions = task.solutions.all()

        if not solutions.exists():
            return Response(
                {'error': 'Для цього завдання ще не визначено правильних рішень'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not language:
            language = self.get_language_from_test(task.test)

        normalized_submitted = self.normalize_code(submitted_code, language)

        print(f"Language: {language}")
        print(f"Normalized submitted code: {normalized_submitted[:50]}...")

        is_correct = False
        correct_solution = None

        for solution in solutions:
            normalized_solution = self.normalize_code(solution.solution_code, language)
            print(f"Normalized solution: {normalized_solution[:50]}...")

            if normalized_submitted == normalized_solution:
                is_correct = True
                correct_solution = solution
                print("Exact match found!")
                break

            if len(normalized_solution) > 0 and normalized_solution in normalized_submitted:
                is_correct = True
                correct_solution = solution
                print("Solution is contained in submission!")
                break

        if not is_correct:
            for solution in solutions:
                if solution.is_primary:
                    key_logic_parts = self.extract_key_logic(solution.solution_code, language)
                    missing_parts = []

                    for part in key_logic_parts:
                        normalized_part = self.normalize_code(part, language)
                        if normalized_part and normalized_part not in normalized_submitted:
                            missing_parts.append(part)
                            print(f"Missing part: {normalized_part[:30]}...")
                        else:
                            print(f"Found part: {normalized_part[:30]}...")

                    if not missing_parts or not key_logic_parts:
                        is_correct = True
                        correct_solution = solution
                        print("All key logic parts found!")
                        break

        attempt = TaskAttempt.objects.create(
            user=request.user,
            task=task,
            submitted_code=submitted_code,
            is_correct=is_correct
        )

        if is_correct:
            progress, created = UserTaskProgress.objects.get_or_create(
                user=request.user,
                test=task.test,
                defaults={'total_tasks': InteractiveTask.objects.filter(test=task.test).count()}
            )

            if created:
                progress.completed_tasks = 1
            else:
                if not TaskAttempt.objects.filter(
                        user=request.user,
                        task=task,
                        is_correct=True
                ).exclude(id=attempt.id).exists():
                    progress.completed_tasks += 1

            if progress.completed_tasks > progress.total_tasks:
                progress.completed_tasks = progress.total_tasks

            progress.save()

        hint = None
        if not is_correct:
            solutions_with_hints = solutions.filter(hint__isnull=False)
            if solutions_with_hints.exists():
                hint = solutions_with_hints.first().hint

            primary_with_hint = solutions.filter(is_primary=True, hint__isnull=False)
            if primary_with_hint.exists():
                hint = primary_with_hint.first().hint

        response_data = {
            'is_correct': is_correct,
            'hint': hint,
            'attempt_id': attempt.id
        }

        if is_correct:
            try:
                from .serializers import TaskSolutionSerializer
                solutions_data = TaskSolutionSerializer(task.solutions.all(), many=True).data
                response_data['solutions'] = solutions_data
            except Exception as e:
                print(f"Error serializing solutions: {str(e)}")

        if is_correct and correct_solution:
            response_data['solution'] = {
                'solution_code': correct_solution.solution_code,
                'code': correct_solution.solution_code,
                'hint': correct_solution.hint
            }

        return Response(response_data)

    def get_language_from_test(self, test):
        icon = test.icon.lower() if hasattr(test, 'icon') else ""
        title = test.title.lower() if hasattr(test, 'title') else ""

        if "html" in icon or "html" in title:
            return "html"
        elif "css" in icon or "css" in title:
            return "css"
        elif "js" in icon or "javascript" in title:
            return "javascript"
        elif "react" in icon or "react" in title:
            return "javascript"
        elif "database" in icon or "sql" in icon or "sql" in title:
            return "sql"
        elif "django" in icon or "python" in icon or "python" in title or "django" in title:
            return "python"
        else:
            return "javascript"

    def normalize_code(self, code, language):
        if not code:
            return ""

        normalized = code.replace('\\n', '\n').replace('\r\n', '\n').replace('\r', '\n')

        lines = []
        in_multiline_comment = False

        for line in normalized.split('\n'):
            stripped = line.strip()

            if not stripped:
                continue

            if language in ["javascript", "react", "css"]:
                if stripped.startswith('//'):
                    continue

                if in_multiline_comment:
                    if "*/" in stripped:
                        in_multiline_comment = False
                        remaining = stripped.split("*/", 1)[1].strip()
                        if remaining:
                            lines.append(remaining)
                    continue

                if "/*" in stripped:
                    in_multiline_comment = True
                    parts = stripped.split("/*", 1)
                    if parts[0].strip():
                        lines.append(parts[0].strip())
                    if "*/" in parts[1]:
                        in_multiline_comment = False
                        remaining = parts[1].split("*/", 1)[1].strip()
                        if remaining:
                            lines.append(remaining)
                    continue

                if '//' in stripped:
                    stripped = stripped.split('//')[0].strip()

            elif language in ["python", "django"]:
                if stripped.startswith('#'):
                    continue

                if '#' in stripped:
                    parts = []
                    in_string = False
                    string_char = None
                    i = 0

                    while i < len(stripped):
                        char = stripped[i]
                        if char in ["'", '"'] and (i == 0 or stripped[i - 1] != '\\'):
                            if not in_string:
                                in_string = True
                                string_char = char
                            elif string_char == char:
                                in_string = False
                        elif char == '#' and not in_string:
                            parts.append(stripped[:i].strip())
                            break
                        i += 1

                    if parts:
                        stripped = parts[0]

            elif language == "html":
                if stripped.startswith('<!--'):
                    if '-->' in stripped:
                        remaining = stripped.split('-->', 1)[1].strip()
                        if remaining:
                            lines.append(remaining)
                    else:
                        in_multiline_comment = True
                    continue

                if in_multiline_comment:
                    if '-->' in stripped:
                        in_multiline_comment = False
                        remaining = stripped.split('-->', 1)[1].strip()
                        if remaining:
                            lines.append(remaining)
                    continue

            elif language == "sql":
                if stripped.startswith('--'):
                    continue

                if ' --' in stripped:
                    stripped = stripped.split(' --')[0].strip()

                if in_multiline_comment:
                    if "*/" in stripped:
                        in_multiline_comment = False
                        remaining = stripped.split("*/", 1)[1].strip()
                        if remaining:
                            lines.append(remaining)
                    continue

                if "/*" in stripped:
                    in_multiline_comment = True
                    parts = stripped.split("/*", 1)
                    if parts[0].strip():
                        lines.append(parts[0].strip())
                    if "*/" in parts[1]:
                        in_multiline_comment = False
                        remaining = parts[1].split("*/", 1)[1].strip()
                        if remaining:
                            lines.append(remaining)
                    continue

            lines.append(stripped)

        if language in ["javascript", "react"]:
            import re
            normalized_lines = []
            for line in lines:
                line = re.sub(r'(let|const|var)(\s+\w+\s*=)', r'var_decl\2', line)
                normalized_lines.append(line)
            lines = normalized_lines

        if language in ["html", "css"]:
            code_only = ''.join(lines)
            import re
            code_only = re.sub(r'\s+', ' ', code_only)
            code_only = re.sub(r'>\s+<', '><', code_only)
            code_only = re.sub(r'\s*:\s*', ':', code_only)
            code_only = re.sub(r'\s*;\s*', ';', code_only)
            code_only = re.sub(r'\s*{\s*', '{', code_only)
            code_only = re.sub(r'\s*}\s*', '}', code_only)
        elif language == "sql":
            code_only = ' '.join(lines).lower()
            import re
            code_only = re.sub(r'\s+', ' ', code_only)
            code_only = re.sub(r'\s*,\s*', ',', code_only)
            code_only = re.sub(r'\s*=\s*', '=', code_only)
            code_only = code_only.strip()
        else:
            code_only = ''.join(lines).replace(' ', '').replace('\t', '')

        return code_only

    def extract_key_logic(self, solution_code, language):
        if not solution_code:
            return []

        lines = solution_code.split('\n')
        key_parts = []
        current_part = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_part:
                    key_parts.append('\n'.join(current_part))
                    current_part = []
                continue

            if (language in ["javascript", "react", "css"] and (
                    stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*/'))) or \
                    (language in ["python", "django"] and stripped.startswith('#')) or \
                    (language == "html" and stripped.startswith('<!--')) or \
                    (language == "sql" and (stripped.startswith('--') or stripped.startswith('/*'))):
                if current_part:
                    key_parts.append('\n'.join(current_part))
                    current_part = []
                continue

            current_part.append(line)

        if current_part:
            key_parts.append('\n'.join(current_part))
        return key_parts


class UserTaskProgressListView(generics.ListAPIView):
    serializer_class = UserTaskProgressSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return UserTaskProgress.objects.none()

        queryset = UserTaskProgress.objects.filter(user=self.request.user)

        if not queryset.exists():
            tests_with_tasks = Test.objects.filter(interactive_tasks__isnull=False).distinct()

            for test in tests_with_tasks:
                total_tasks = InteractiveTask.objects.filter(test=test).count()
                if total_tasks > 0:
                    UserTaskProgress.objects.create(
                        user=self.request.user,
                        test=test,
                        total_tasks=total_tasks,
                        completed_tasks=0
                    )

            queryset = UserTaskProgress.objects.filter(user=self.request.user)

        return queryset


class UserTaskProgressDetailView(generics.RetrieveAPIView):
    serializer_class = UserTaskProgressSerializer
    permission_classes = (permissions.AllowAny,)

    def get_object(self):
        test_id = self.kwargs.get('test_id')
        test = get_object_or_404(Test, id=test_id)

        if not self.request.user.is_authenticated:
            return UserTaskProgress(
                test=test,
                completed_tasks=0,
                total_tasks=InteractiveTask.objects.filter(test=test).count(),
                user=None
            )

        progress, created = UserTaskProgress.objects.get_or_create(
            user=self.request.user,
            test=test,
            defaults={
                'total_tasks': InteractiveTask.objects.filter(test=test).count()
            }
        )

        if progress.total_tasks != InteractiveTask.objects.filter(test=test).count():
            progress.total_tasks = InteractiveTask.objects.filter(test=test).count()
            progress.save()

        return progress

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if not request.user.is_authenticated and not instance.pk:
                test_id = self.kwargs.get('test_id')
                test = get_object_or_404(Test, id=test_id)

                return Response({
                    'test': test.id,
                    'test_title': test.title,
                    'completed_tasks': 0,
                    'total_tasks': InteractiveTask.objects.filter(test=test).count(),
                    'completion_percentage': 0,
                    'last_updated': None
                })

            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except Exception as e:
            print(f"Error retrieving task progress: {str(e)}")
            test_id = self.kwargs.get('test_id')
            if test_id:
                test = get_object_or_404(Test, id=test_id)
                return Response({
                    'test': test.id,
                    'test_title': test.title,
                    'completed_tasks': 0,
                    'total_tasks': InteractiveTask.objects.filter(test=test).count(),
                    'completion_percentage': 0,
                    'last_updated': None
                })
            return Response({
                'error': 'An error occurred while retrieving progress'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskAttemptListView(generics.ListAPIView):
    serializer_class = TaskAttemptSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        test_id = self.kwargs.get('test_id')
        task_id = self.kwargs.get('task_id')

        queryset = TaskAttempt.objects.filter(user=self.request.user)

        if test_id:
            queryset = queryset.filter(task__test_id=test_id)
        if task_id:
            queryset = queryset.filter(task_id=task_id)

        return queryset.order_by('-completed_at')