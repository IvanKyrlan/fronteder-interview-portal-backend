# # core/views.py
#
# from rest_framework import generics, permissions, status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework.permissions import AllowAny
# from django.contrib.auth import authenticate
# from django.contrib.auth.models import User
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from django.views.decorators.http import require_http_methods
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# from django.core.cache import cache
# from datetime import datetime
# from django.contrib.contenttypes.models import ContentType
# from django.db import models
# import re
# import json
# import tempfile
# import subprocess
# import os
# from .serializers import (
#     UserSerializer,
#     RegisterSerializer,
#     UserProgressSerializer,
#     ChangePasswordSerializer,
#     TestSerializer, TestDetailSerializer,
#     TestAttemptSerializer,
#     InteractiveTaskSerializer,
#     InteractiveTaskDetailSerializer,
#     TaskAttemptSerializer,
#     SubmitTaskSerializer,
#     UserTaskProgressSerializer,
#     ArticleListSerializer,
#     ArticleDetailSerializer,
#     CommentSerializer,
#     CommentCreateSerializer,
#     InterviewVideoSerializer,
#     ForumTopicSerializer,
# )
# from .models import UserProgress, Test, Question, TestAttempt, InteractiveTask, TaskSolution, TaskAttempt, UserTaskProgress, Article, Comment, InterviewVideo, ForumTopic
#
#
# @csrf_exempt
# @require_http_methods(["OPTIONS"])
# def cors_preflight(request):
#     response = HttpResponse()
#     response["Access-Control-Allow-Origin"] = "http://localhost:5173"
#     response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
#     response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
#     response["Access-Control-Allow-Credentials"] = "true"
#     return response
#
#
# @method_decorator(csrf_exempt, name='dispatch')
# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     permission_classes = (permissions.AllowAny,)
#     serializer_class = RegisterSerializer
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         user = serializer.save()
#         refresh = RefreshToken.for_user(user)
#
#         response_data = {
#             'user': UserSerializer(user).data,
#             'token': str(refresh.access_token),
#             'refresh': str(refresh)
#         }
#
#         return Response(response_data, status=status.HTTP_201_CREATED)
#
#
# @method_decorator(csrf_exempt, name='dispatch')
# class LoginView(APIView):
#     permission_classes = (permissions.AllowAny,)
#
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#
#         if not username or not password:
#             return Response({'error': 'Потрібно вказати логін та пароль'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         # Спроба аутентифікації за username
#         user = authenticate(username=username, password=password)
#
#         # Якщо не вдалося, спробуємо за email
#         if not user and '@' in username:
#             try:
#                 user_obj = User.objects.get(email=username)
#                 user = authenticate(username=user_obj.username, password=password)
#             except User.DoesNotExist:
#                 pass
#
#         if user:
#             refresh = RefreshToken.for_user(user)
#             return Response({
#                 'user': UserSerializer(user).data,
#                 'token': str(refresh.access_token),
#                 'refresh': str(refresh)
#             })
#         else:
#             return Response(
#                 {'error': 'Невірний логін або пароль'},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )
#
#
# class UserProfileView(generics.RetrieveUpdateAPIView):
#     serializer_class = UserSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_object(self):
#         return self.request.user
#
#
# class ChangePasswordView(APIView):
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def post(self, request):
#         serializer = ChangePasswordSerializer(
#             data=request.data,
#             context={'request': request}
#         )
#
#         if serializer.is_valid():
#             user = request.user
#             user.set_password(serializer.validated_data['new_password'])
#             user.save()
#             return Response({'message': 'Пароль успішно змінено'})
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class UserProgressListView(generics.ListAPIView):
#     serializer_class = UserProgressSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_queryset(self):
#         return UserProgress.objects.filter(user=self.request.user)
#
#
# class TestListView(generics.ListAPIView):
#     queryset = Test.objects.all()
#     serializer_class = TestSerializer
#     permission_classes = (permissions.AllowAny,)
#
#
# class TestDetailView(generics.RetrieveAPIView):
#     queryset = Test.objects.all()
#     serializer_class = TestDetailSerializer
#     permission_classes = (permissions.AllowAny,)
#
#     def retrieve(self, request, *args, **kwargs):
#         test = self.get_object()
#
#         # Отримуємо випадкові питання для тесту (без кешування)
#         questions = Question.objects.filter(test=test).order_by('?')[:test.questions]
#
#         formatted_questions = []
#         for idx, q in enumerate(questions):
#             # Отримуємо відповіді
#             answers = list(q.answers.filter(text__isnull=False).exclude(text__exact=''))
#
#             # Переконуємося, що є рівно 4 відповіді
#             if len(answers) != 4:
#                 print(f"Warning: Question {q.id} has {len(answers)} answers, expected 4. Skipping.")
#                 continue
#
#             # Знаходимо правильну відповідь
#             correct_answers = [a for a in answers if a.is_correct]
#
#             # Якщо немає правильної відповіді або більше однієї правильної
#             if len(correct_answers) != 1:
#                 if len(correct_answers) == 0 and answers:
#                     # Встановлюємо першу як правильну
#                     answers[0].is_correct = True
#                     answers[0].save()
#                     correct_answer_idx = 0
#                     print(f"Warning: Question {q.id} had no correct answer, set first as correct")
#                 elif len(correct_answers) > 1:
#                     # Залишаємо тільки першу правильну
#                     for a in correct_answers[1:]:
#                         a.is_correct = False
#                         a.save()
#                     correct_answer_idx = answers.index(correct_answers[0])
#                     print(f"Warning: Question {q.id} had multiple correct answers, keeping only first")
#             else:
#                 # Нормальний випадок - одна правильна відповідь
#                 correct_answer_idx = answers.index(correct_answers[0])
#
#             # Форматуємо відповіді як масив текстів
#             formatted_answers = [a.text for a in answers]
#
#             formatted_questions.append({
#                 'id': idx,
#                 'question': q.question,
#                 'answers': formatted_answers,
#                 'correctAnswerId': correct_answer_idx
#             })
#
#         response_data = {
#             'id': test.id,
#             'title': test.title,
#             'icon': test.icon,
#             'color': test.color,
#             'questions': formatted_questions,
#             'duration': test.duration,
#             'description': test.description,
#         }
#
#         return Response(response_data)
#
#
# class UserProgressListCreateView(generics.ListCreateAPIView):
#     serializer_class = UserProgressSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_queryset(self):
#         return UserProgress.objects.filter(user=self.request.user).select_related('test')
#
#     def create(self, request, *args, **kwargs):
#         test_id = request.data.get('test_id')
#         score = request.data.get('score')  # відсоток
#         correct_answers = request.data.get('correct_answers')  # правильні відповіді
#         total_questions = request.data.get('total_questions')  # загальна кількість питань
#
#         try:
#             test = Test.objects.get(id=test_id)
#
#             # Створюємо запис про спробу
#             test_attempt = TestAttempt.objects.create(
#                 user=request.user,
#                 test=test,
#                 score=score,
#                 correct_answers=correct_answers,
#                 total_questions=total_questions
#             )
#
#             # UserProgress оновлюється автоматично в save() методі TestAttempt
#
#             # Отримуємо оновлений UserProgress
#             progress = UserProgress.objects.get(user=request.user, test=test)
#             serializer = self.get_serializer(progress)
#
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         except Test.DoesNotExist:
#             return Response(
#                 {'error': 'Test not found'},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#
# class TestAttemptListView(generics.ListAPIView):
#     serializer_class = TestAttemptSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_queryset(self):
#         test_id = self.kwargs.get('test_id')
#         return TestAttempt.objects.filter(
#             user=self.request.user,
#             test_id=test_id
#         ).order_by('-completed_at')
#
#
# class UserProgressDetailView(generics.RetrieveAPIView):
#     serializer_class = UserProgressSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_object(self):
#         test_id = self.kwargs.get('test_id')
#         return get_object_or_404(
#             UserProgress,
#             user=self.request.user,
#             test_id=test_id
#         )
#
#
# class InteractiveTaskListView(generics.ListAPIView):
#     """API для отримання списку інтерактивних завдань для тесту"""
#     serializer_class = InteractiveTaskDetailSerializer
#     permission_classes = (permissions.AllowAny,)  # Дозволяємо доступ всім, як і для звичайних тестів
#
#     def get_queryset(self):
#         test_id = self.kwargs.get('test_id')
#         return InteractiveTask.objects.filter(test_id=test_id)
#
#
# class InteractiveTaskDetailView(generics.RetrieveAPIView):
#     """API для отримання деталей одного інтерактивного завдання"""
#     queryset = InteractiveTask.objects.all()
#     serializer_class = InteractiveTaskDetailSerializer
#     permission_classes = (permissions.AllowAny,)
#
#
# class SubmitTaskView(APIView):
#     """API для відправлення рішення завдання на перевірку"""
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def post(self, request):
#         serializer = SubmitTaskSerializer(data=request.data)
#
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#         task_id = serializer.validated_data['task_id']
#         submitted_code = serializer.validated_data['code']
#         # Get language from request if provided, otherwise we'll detect it
#         language = serializer.validated_data.get('language', None)
#
#         # Отримуємо завдання
#         task = get_object_or_404(InteractiveTask, id=task_id)
#
#         # Отримуємо всі можливі рішення
#         solutions = task.solutions.all()
#
#         if not solutions.exists():
#             return Response(
#                 {'error': 'Для цього завдання ще не визначено правильних рішень'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Якщо мова не вказана, визначаємо її на основі тесту
#         if not language:
#             language = self.get_language_from_test(task.test)
#
#         # Нормалізуємо переноси рядків та видаляємо зайві пробіли для коректного порівняння
#         normalized_submitted = self.normalize_code(submitted_code, language)
#
#         # Для відладки
#         print(f"Language: {language}")
#         print(f"Normalized submitted code: {normalized_submitted[:50]}...")
#
#         # Перевіряємо рішення користувача
#         is_correct = False
#         correct_solution = None
#
#         for solution in solutions:
#             normalized_solution = self.normalize_code(solution.solution_code, language)
#             print(f"Normalized solution: {normalized_solution[:50]}...")
#
#             # Перевіряємо на точне співпадіння
#             if normalized_submitted == normalized_solution:
#                 is_correct = True
#                 correct_solution = solution
#                 print("Exact match found!")
#                 break
#
#             # Перевіряємо, чи міститься рішення в коді користувача (може бути зайвий код)
#             if len(normalized_solution) > 0 and normalized_solution in normalized_submitted:
#                 is_correct = True
#                 correct_solution = solution
#                 print("Solution is contained in submission!")
#                 break
#
#         # Якщо користувач не має точного співпадіння, перевіряємо, чи міститься ключова логіка
#         if not is_correct:
#             for solution in solutions:
#                 # Отримуємо первинне рішення для перевірки ключової логіки
#                 if solution.is_primary:
#                     # Знаходимо ключові частини коду, які мають бути присутні
#                     key_logic_parts = self.extract_key_logic(solution.solution_code, language)
#                     missing_parts = []
#
#                     for part in key_logic_parts:
#                         normalized_part = self.normalize_code(part, language)
#                         if normalized_part and normalized_part not in normalized_submitted:
#                             missing_parts.append(part)
#                             print(f"Missing part: {normalized_part[:30]}...")
#                         else:
#                             print(f"Found part: {normalized_part[:30]}...")
#
#                     # Якщо всі ключові частини присутні або список частей пуст, рішення вважається правильним
#                     if not missing_parts or not key_logic_parts:
#                         is_correct = True
#                         correct_solution = solution
#                         print("All key logic parts found!")
#                         break
#
#         # Зберігаємо спробу користувача
#         attempt = TaskAttempt.objects.create(
#             user=request.user,
#             task=task,
#             submitted_code=submitted_code,
#             is_correct=is_correct
#         )
#
#         # Якщо рішення правильне, оновлюємо прогрес користувача
#         if is_correct:
#             progress, created = UserTaskProgress.objects.get_or_create(
#                 user=request.user,
#                 test=task.test,
#                 defaults={'total_tasks': InteractiveTask.objects.filter(test=task.test).count()}
#             )
#
#             if created:
#                 progress.completed_tasks = 1
#             else:
#                 # Перевіряємо, чи це завдання вже було враховано в прогресі
#                 if not TaskAttempt.objects.filter(
#                         user=request.user,
#                         task=task,
#                         is_correct=True
#                 ).exclude(id=attempt.id).exists():
#                     progress.completed_tasks += 1
#
#             # Перевіряємо, чи не перевищує кількість виконаних завдань загальну кількість
#             if progress.completed_tasks > progress.total_tasks:
#                 progress.completed_tasks = progress.total_tasks
#
#             progress.save()
#
#         # Знаходимо підказку для відображення користувачу
#         hint = None
#         if not is_correct:
#             # Спочатку шукаємо загальну підказку
#             solutions_with_hints = solutions.filter(hint__isnull=False)
#             if solutions_with_hints.exists():
#                 hint = solutions_with_hints.first().hint
#
#             # Якщо є первинне рішення з підказкою, використовуємо його
#             primary_with_hint = solutions.filter(is_primary=True, hint__isnull=False)
#             if primary_with_hint.exists():
#                 hint = primary_with_hint.first().hint
#
#         response_data = {
#             'is_correct': is_correct,
#             'hint': hint,
#             'attempt_id': attempt.id
#         }
#
#         # Add solutions only if the task was solved correctly
#         if is_correct:
#             try:
#                 # Use a try-except block to prevent errors
#                 solutions_data = TaskSolutionSerializer(task.solutions.all(), many=True).data
#                 response_data['solutions'] = solutions_data
#             except Exception as e:
#                 print(f"Error serializing solutions: {str(e)}")
#
#         # Keep single solution for backward compatibility
#         if is_correct and correct_solution:
#             response_data['solution'] = {
#                 'solution_code': correct_solution.solution_code,
#                 'code': correct_solution.solution_code,
#                 'hint': correct_solution.hint
#             }
#
#         return Response(response_data)
#
#     def get_language_from_test(self, test):
#         """Визначає мову програмування на основі тесту"""
#         # Визначаємо мову за назвою або іконкою тесту
#         icon = test.icon.lower() if hasattr(test, 'icon') else ""
#         title = test.title.lower() if hasattr(test, 'title') else ""
#
#         if "html" in icon or "html" in title:
#             return "html"
#         elif "css" in icon or "css" in title:
#             return "css"
#         elif "js" in icon or "javascript" in title:
#             return "javascript"
#         elif "react" in icon or "react" in title:
#             return "javascript"  # React використовує JavaScript
#         elif "database" in icon or "sql" in icon or "sql" in title:
#             return "sql"
#         elif "django" in icon or "python" in icon or "python" in title or "django" in title:
#             return "python"
#         else:
#             return "javascript"  # За замовчуванням
#
#     def normalize_code(self, code, language):
#         """Нормалізує код для порівняння в залежності від мови програмування"""
#         if not code:
#             return ""
#
#         # Нормалізуємо переноси рядків
#         normalized = code.replace('\\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
#
#         # Видаляємо коментарі та форматування в залежності від мови
#         lines = []
#         in_multiline_comment = False
#
#         for line in normalized.split('\n'):
#             stripped = line.strip()
#
#             # Пропускаємо порожні рядки
#             if not stripped:
#                 continue
#
#             # Обробка коментарів залежно від мови
#             if language in ["javascript", "react", "css"]:
#                 # Пропускаємо рядки, що містять тільки однорядкові коментарі
#                 if stripped.startswith('//'):
#                     continue
#
#                 # Обробка багаторядкових коментарів
#                 if in_multiline_comment:
#                     if "*/" in stripped:
#                         in_multiline_comment = False
#                         # Якщо після закриття коментаря є код, додаємо його
#                         remaining = stripped.split("*/", 1)[1].strip()
#                         if remaining:
#                             lines.append(remaining)
#                     continue
#
#                 if "/*" in stripped:
#                     in_multiline_comment = True
#                     # Якщо перед відкриттям коментаря є код, додаємо його
#                     parts = stripped.split("/*", 1)
#                     if parts[0].strip():
#                         lines.append(parts[0].strip())
#                     # Якщо коментар закривається в тому ж рядку
#                     if "*/" in parts[1]:
#                         in_multiline_comment = False
#                         # Якщо після закриття коментаря є код, додаємо його
#                         remaining = parts[1].split("*/", 1)[1].strip()
#                         if remaining:
#                             lines.append(remaining)
#                     continue
#
#                 # Видаляємо однорядкові коментарі з кінця рядка
#                 if '//' in stripped:
#                     stripped = stripped.split('//')[0].strip()
#
#             elif language in ["python", "django"]:
#                 # Пропускаємо рядки, що містять тільки однорядкові коментарі
#                 if stripped.startswith('#'):
#                     continue
#
#                 # Видаляємо однорядкові коментарі з кінця рядка
#                 if '#' in stripped:
#                     # Перевіряємо, чи не є символ # частиною рядка
#                     parts = []
#                     in_string = False
#                     string_char = None
#                     i = 0
#
#                     while i < len(stripped):
#                         char = stripped[i]
#                         # Перевірка початку/кінця рядка
#                         if char in ["'", '"'] and (i == 0 or stripped[i - 1] != '\\'):
#                             if not in_string:
#                                 in_string = True
#                                 string_char = char
#                             elif string_char == char:
#                                 in_string = False
#                         # Знаходження # не в рядку
#                         elif char == '#' and not in_string:
#                             parts.append(stripped[:i].strip())
#                             break
#                         i += 1
#
#                     if parts:
#                         stripped = parts[0]
#
#             elif language == "html":
#                 # Пропускаємо HTML-коментарі
#                 if stripped.startswith('<!--'):
#                     if '-->' in stripped:
#                         # Якщо коментар закінчується в тому ж рядку
#                         remaining = stripped.split('-->', 1)[1].strip()
#                         if remaining:
#                             lines.append(remaining)
#                     else:
#                         in_multiline_comment = True
#                     continue
#
#                 if in_multiline_comment:
#                     if '-->' in stripped:
#                         in_multiline_comment = False
#                         remaining = stripped.split('-->', 1)[1].strip()
#                         if remaining:
#                             lines.append(remaining)
#                     continue
#
#             elif language == "sql":
#                 # Пропускаємо SQL однорядкові коментарі
#                 if stripped.startswith('--'):
#                     continue
#
#                 # Видаляємо однорядкові коментарі з кінця рядка
#                 if ' --' in stripped:
#                     stripped = stripped.split(' --')[0].strip()
#
#                 # Обробка багаторядкових коментарів у SQL
#                 if in_multiline_comment:
#                     if "*/" in stripped:
#                         in_multiline_comment = False
#                         remaining = stripped.split("*/", 1)[1].strip()
#                         if remaining:
#                             lines.append(remaining)
#                     continue
#
#                 if "/*" in stripped:
#                     in_multiline_comment = True
#                     parts = stripped.split("/*", 1)
#                     if parts[0].strip():
#                         lines.append(parts[0].strip())
#                     if "*/" in parts[1]:
#                         in_multiline_comment = False
#                         remaining = parts[1].split("*/", 1)[1].strip()
#                         if remaining:
#                             lines.append(remaining)
#                     continue
#
#             # Додаємо очищений рядок
#             lines.append(stripped)
#
#         # Нормалізація різних оголошень змінних для JavaScript
#         if language in ["javascript", "react"]:
#             import re
#             normalized_lines = []
#             for line in lines:
#                 # Normalize variable declarations (let/const/var become the same)
#                 line = re.sub(r'(let|const|var)(\s+\w+\s*=)', r'var_decl\2', line)
#                 normalized_lines.append(line)
#             lines = normalized_lines
#
#         # Об'єднуємо код і видаляємо всі пробіли для порівняння
#         # В залежності від мови, можемо застосувати додаткову нормалізацію
#         if language in ["html", "css"]:
#             # Для HTML і CSS зберігаємо пробіли в значущих місцях
#             code_only = ''.join(lines)
#             # Видаляємо зайві пробіли
#             import re
#             code_only = re.sub(r'\s+', ' ', code_only)  # Замінюємо кілька пробілів одним
#             code_only = re.sub(r'>\s+<', '><', code_only)  # Видаляємо пробіли між тегами
#             code_only = re.sub(r'\s*:\s*', ':', code_only)  # Нормалізуємо пробіли навколо двокрапки в CSS
#             code_only = re.sub(r'\s*;\s*', ';', code_only)  # Нормалізуємо пробіли навколо крапки з комою
#             code_only = re.sub(r'\s*{\s*', '{', code_only)  # Нормалізуємо пробіли навколо фігурних дужок
#             code_only = re.sub(r'\s*}\s*', '}', code_only)
#         elif language == "sql":
#             # Для SQL нормалізуємо ключові слова та видаляємо пробіли
#             code_only = ' '.join(lines).lower()  # SQL не чутливий до регістру
#             # Нормалізуємо синтаксис SQL
#             import re
#             code_only = re.sub(r'\s+', ' ', code_only)  # Замінюємо кілька пробілів одним
#             code_only = re.sub(r'\s*,\s*', ',', code_only)  # Нормалізуємо пробіли навколо ком
#             code_only = re.sub(r'\s*=\s*', '=', code_only)  # Нормалізуємо пробіли навколо знаку рівності
#             code_only = code_only.strip()
#         else:
#             # Для інших мов видаляємо всі пробіли
#             code_only = ''.join(lines).replace(' ', '').replace('\t', '')
#
#         return code_only
#
#     def extract_key_logic(self, solution_code, language):
#         """Витягує ключові частини логіки з рішення в залежності від мови програмування"""
#         if not solution_code:
#             return []
#
#         # Розділяємо код на логічні блоки
#         lines = solution_code.split('\n')
#         key_parts = []
#         current_part = []
#
#         for line in lines:
#             stripped = line.strip()
#             # Пропускаємо коментарі та порожні рядки
#             if not stripped:
#                 if current_part:  # Якщо у нас є накопичений блок, зберігаємо його
#                     key_parts.append('\n'.join(current_part))
#                     current_part = []
#                 continue
#
#             # Пропускаємо коментарі в залежності від мови
#             if (language in ["javascript", "react", "css"] and (
#                     stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*/'))) or \
#                     (language in ["python", "django"] and stripped.startswith('#')) or \
#                     (language == "html" and stripped.startswith('<!--')) or \
#                     (language == "sql" and (stripped.startswith('--') or stripped.startswith('/*'))):
#                 if current_part:
#                     key_parts.append('\n'.join(current_part))
#                     current_part = []
#                 continue
#
#             current_part.append(line)
#
#         # Додаємо останній блок, якщо він існує
#         if current_part:
#             key_parts.append('\n'.join(current_part))
#
#         # Якщо в рішенні є тільки один блок, розбиваємо його на дрібніші частини відповідно до мови
#         if len(key_parts) <= 1 and solution_code:
#             import re
#
#             if language in ["javascript", "react"]:
#                 # Normalize variable declarations to handle let/const/var differences
#                 normalized_code = re.sub(r'(let|const|var)\s+(\w+\s*=)', r'var_decl \2', solution_code)
#
#                 # Знаходимо всі блоки if/for/while/function - структура циклів та умовних операторів
#                 control_structures = re.findall(r'((?:if|for|while|function\s+\w+)\s*\([^{]*\)\s*\{)', normalized_code)
#                 if control_structures:
#                     key_parts.extend(control_structures)
#
#                 # Знаходимо основні операції в циклах/умовах (ключова логіка алгоритму)
#                 loop_operations = re.findall(r'for\s*\([^)]*\)\s*\{[^}]*\}', normalized_code)
#                 if loop_operations:
#                     for op in loop_operations:
#                         # Extract the core logic inside loops (what actually happens in each iteration)
#                         inner_operations = re.findall(r'\s+([\w.]+(?:\([^)]*\)|\[[^\]]*\])[^;]*;)', op)
#                         if inner_operations:
#                             key_parts.extend(inner_operations)
#
#                 # Знаходимо логіку повернення результатів
#                 returns = re.findall(r'return\s+([^;]+);', normalized_code)
#                 if returns:
#                     key_parts.extend([f"return {r};" for r in returns])
#
#                 # Знаходимо основні маніпуляції з масивами (push, pop, etc.)
#                 array_ops = re.findall(r'([\w.]+\.(?:push|pop|shift|unshift|splice|slice|map|filter|reduce)\([^)]*\))',
#                                        normalized_code)
#                 if array_ops:
#                     key_parts.extend(array_ops)
#
#             elif language in ["python", "django"]:
#                 # Normalize Python variable declarations
#                 normalized_code = solution_code
#
#                 # Знаходимо основну структуру (функції, цикли, умови)
#                 functions = re.findall(r'def\s+(\w+)\s*\([^)]*\)\s*:', normalized_code)
#                 if functions:
#                     key_parts.extend([f"def {func}" for func in functions])
#
#                 # Витягуємо логіку циклів
#                 loop_structures = re.findall(r'(for\s+\w+\s+in\s+[^:]+:)', normalized_code)
#                 if loop_structures:
#                     key_parts.extend(loop_structures)
#
#                 # Витягуємо операції з списками
#                 list_ops = re.findall(r'(\w+\.(?:append|extend|pop|remove|insert)\([^)]*\))', normalized_code)
#                 if list_ops:
#                     key_parts.extend(list_ops)
#
#                 # Знаходимо логіку повернення результатів
#                 returns = re.findall(r'return\s+([^\n]+)', normalized_code)
#                 if returns:
#                     key_parts.extend([f"return {r}" for r in returns])
#
#             elif language == "html":
#                 # Залишаємо попередню логіку для HTML
#                 tags = re.findall(r'(<\w+[^>]*>.*?</\w+>)', solution_code, re.DOTALL)
#                 if tags:
#                     key_parts.extend(tags)
#
#                 self_closing_tags = re.findall(r'(<\w+[^>]*/?>)', solution_code)
#                 if self_closing_tags:
#                     key_parts.extend(self_closing_tags)
#
#                 # Focus on the structure rather than specific attributes
#                 structure_elements = re.findall(r'<(\w+)[^>]*>', solution_code)
#                 if structure_elements:
#                     key_parts.extend([f"<{elem}>" for elem in set(structure_elements)])
#
#             elif language == "css":
#                 # Залишаємо попередню логіку для CSS
#                 rules = re.findall(r'([^{]+\{[^}]*\})', solution_code)
#                 if rules:
#                     key_parts.extend(rules)
#
#                 # Focus on the selectors and key properties
#                 selectors = re.findall(r'([^{,]+)\s*{', solution_code)
#                 if selectors:
#                     key_parts.extend([s.strip() for s in selectors])
#
#                 # Extract important properties
#                 properties = re.findall(r'([\w-]+\s*:\s*[^;]+;)', solution_code)
#                 if properties:
#                     key_parts.extend(properties)
#
#             elif language == "sql":
#                 # Залишаємо попередню логіку для SQL
#                 normalized_code = solution_code.lower()  # SQL is case-insensitive
#
#                 # Focus on the query structure and keywords
#                 query_types = re.findall(r'(select|insert|update|delete|create|alter)\s+', normalized_code,
#                                          re.IGNORECASE)
#                 if query_types:
#                     for qt in set(query_types):
#                         key_parts.append(qt.upper())
#
#                 # Extract the tables involved
#                 tables = re.findall(r'from\s+(\w+)', normalized_code, re.IGNORECASE)
#                 if tables:
#                     key_parts.extend([f"FROM {t}" for t in set(tables)])
#
#                 # Extract conditions
#                 conditions = re.findall(r'where\s+([^;()]+?)(group|order|limit|$)', normalized_code, re.IGNORECASE)
#                 if conditions:
#                     key_parts.extend([f"WHERE {c[0].strip()}" for c in conditions])
#
#         # Remove duplicates while preserving order
#         seen = set()
#         key_parts = [x for x in key_parts if not (x in seen or seen.add(x))]
#
#         return key_parts
#
#
# class UserTaskProgressListView(generics.ListAPIView):
#     """API для отримання прогресу користувача з інтерактивних завдань"""
#     serializer_class = UserTaskProgressSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_queryset(self):
#         if not self.request.user.is_authenticated:
#             return UserTaskProgress.objects.none()
#
#         queryset = UserTaskProgress.objects.filter(user=self.request.user)
#
#         # Проверяем, есть ли записи прогресса для пользователя
#         if not queryset.exists():
#             # Если нет прогресса, создаем записи для всех тестов, у которых есть интерактивные задания
#             tests_with_tasks = Test.objects.filter(interactive_tasks__isnull=False).distinct()
#
#             for test in tests_with_tasks:
#                 total_tasks = InteractiveTask.objects.filter(test=test).count()
#                 if total_tasks > 0:
#                     UserTaskProgress.objects.create(
#                         user=self.request.user,
#                         test=test,
#                         total_tasks=total_tasks,
#                         completed_tasks=0
#                     )
#
#             # Получаем обновленный queryset
#             queryset = UserTaskProgress.objects.filter(user=self.request.user)
#
#         return queryset
#
#
# class UserTaskProgressDetailView(generics.RetrieveAPIView):
#     """API для отримання детального прогресу користувача для конкретного тесту"""
#     serializer_class = UserTaskProgressSerializer
#     permission_classes = (permissions.AllowAny,)  # Изменено на AllowAny для совместимости с фронтендом
#
#     def get_object(self):
#         test_id = self.kwargs.get('test_id')
#         # Отримати тест
#         test = get_object_or_404(Test, id=test_id)
#
#         # Если пользователь не аутентифицирован, создаем пустой прогресс
#         if not self.request.user.is_authenticated:
#             return UserTaskProgress(
#                 test=test,
#                 completed_tasks=0,
#                 total_tasks=InteractiveTask.objects.filter(test=test).count(),
#                 user=None  # Временно указываем None
#             )
#
#         # Отримати або створити прогрес
#         progress, created = UserTaskProgress.objects.get_or_create(
#             user=self.request.user,
#             test=test,
#             defaults={
#                 'total_tasks': InteractiveTask.objects.filter(test=test).count()
#             }
#         )
#
#         # Якщо прогрес був створений, але всього завдань не вказано або вони змінилися
#         if progress.total_tasks != InteractiveTask.objects.filter(test=test).count():
#             progress.total_tasks = InteractiveTask.objects.filter(test=test).count()
#             progress.save()
#
#         return progress
#
#     def retrieve(self, request, *args, **kwargs):
#         try:
#             instance = self.get_object()
#
#             # Если пользователь не аутентифицирован, возвращаем сериализованный пустой прогресс
#             if not request.user.is_authenticated and not instance.pk:
#                 test_id = self.kwargs.get('test_id')
#                 test = get_object_or_404(Test, id=test_id)
#
#                 return Response({
#                     'test': test.id,
#                     'test_title': test.title,
#                     'completed_tasks': 0,
#                     'total_tasks': InteractiveTask.objects.filter(test=test).count(),
#                     'completion_percentage': 0,
#                     'last_updated': None
#                 })
#
#             serializer = self.get_serializer(instance)
#             return Response(serializer.data)
#
#         except Exception as e:
#             # Обработка ошибок и возврат пустого прогресса
#             print(f"Error retrieving task progress: {str(e)}")
#             test_id = self.kwargs.get('test_id')
#             if test_id:
#                 test = get_object_or_404(Test, id=test_id)
#                 return Response({
#                     'test': test.id,
#                     'test_title': test.title,
#                     'completed_tasks': 0,
#                     'total_tasks': InteractiveTask.objects.filter(test=test).count(),
#                     'completion_percentage': 0,
#                     'last_updated': None
#                 })
#             return Response({
#                 'error': 'An error occurred while retrieving progress'
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
# class TaskAttemptListView(generics.ListAPIView):
#     serializer_class = TaskAttemptSerializer
#     permission_classes = (permissions.IsAuthenticated,)
#
#     def get_queryset(self):
#         test_id = self.kwargs.get('test_id')
#         task_id = self.kwargs.get('task_id')
#
#         queryset = TaskAttempt.objects.filter(user=self.request.user)
#
#         if test_id:
#             queryset = queryset.filter(task__test_id=test_id)
#         if task_id:
#             queryset = queryset.filter(task_id=task_id)
#
#         return queryset.order_by('-completed_at')
#
#
# class ArticleListView(generics.ListAPIView):
#     """API view for listing articles"""
#     queryset = Article.objects.all()
#     serializer_class = ArticleListSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Filter by featured if requested
#         featured = self.request.query_params.get('featured', None)
#         if featured and featured.lower() == 'true':
#             queryset = queryset.filter(featured=True)
#
#         return queryset
#
#
# class ArticleDetailView(generics.RetrieveAPIView):
#     """API view for retrieving a specific article"""
#     queryset = Article.objects.all()
#     serializer_class = ArticleDetailSerializer
#     permission_classes = [permissions.AllowAny]
#     lookup_field = 'slug'  # Use slug instead of ID for SEO-friendly URLs
#
#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         return super().retrieve(request, *args, **kwargs)
#
#
# class CommentListView(generics.ListAPIView):
#     """API view to get comments for specific content"""
#     serializer_class = CommentSerializer
#     permission_classes = [AllowAny]
#
#     def get_queryset(self):
#         content_type_str = self.request.query_params.get('content_type')
#         object_id = self.request.query_params.get('object_id')
#
#         if not content_type_str or not object_id:
#             return Comment.objects.none()
#
#         try:
#             app_label, model = content_type_str.split('.')
#             content_type = ContentType.objects.get(app_label=app_label, model=model)
#             # Only return top-level comments (those without a parent)
#             return Comment.objects.filter(
#                 content_type=content_type,
#                 object_id=object_id,
#                 parent__isnull=True
#             )
#         except (ValueError, ContentType.DoesNotExist):
#             return Comment.objects.none()
#
#
# class CommentCreateView(generics.CreateAPIView):
#     """API view to create a new comment"""
#     serializer_class = CommentCreateSerializer
#     permission_classes = [AllowAny]
#
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             self.perform_create(serializer)
#             # After creating, fetch the full comment with replies
#             comment = Comment.objects.get(id=serializer.instance.id)
#             response_serializer = CommentSerializer(comment)
#             return Response(response_serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class InterviewVideoListView(generics.ListAPIView):
#     """API view for listing interview videos"""
#     queryset = InterviewVideo.objects.all()
#     serializer_class = InterviewVideoSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#
#         # Фільтрація за категорією
#         category = self.request.query_params.get('category', None)
#         if category:
#             queryset = queryset.filter(category=category)
#
#         # Фільтрація за рівнем
#         level = self.request.query_params.get('level', None)
#         if level:
#             queryset = queryset.filter(level=level)
#
#         # Фільтрація за featured
#         featured = self.request.query_params.get('featured', None)
#         if featured and featured.lower() == 'true':
#             queryset = queryset.filter(featured=True)
#
#         return queryset
#
# class InterviewVideoDetailView(generics.RetrieveAPIView):
#     """API view for retrieving a specific interview video"""
#     queryset = InterviewVideo.objects.all()
#     serializer_class = InterviewVideoSerializer
#     permission_classes = [permissions.AllowAny]
#
#
# class ForumTopicListView(generics.ListCreateAPIView):
#     serializer_class = ForumTopicSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def get_queryset(self):
#         queryset = ForumTopic.objects.all()
#
#         # Фільтрація за категорією
#         category = self.request.query_params.get('category', None)
#         if category:
#             queryset = queryset.filter(category=category)
#
#         # Пошук за заголовком або вмістом
#         search = self.request.query_params.get('search', None)
#         if search:
#             queryset = queryset.filter(
#                 models.Q(title__icontains=search) |
#                 models.Q(content__icontains=search)
#             )
#
#         # Обробка сортування
#         sort_by = self.request.query_params.get('sort_by', None)
#         if sort_by:
#             # Безпечна обробка параметрів сортування
#             sort_mapping = {
#                 'newest': '-created_at',  # За датою створення (найновіші спочатку)
#                 'oldest': 'created_at',  # За датою створення (найстаріші спочатку)
#                 'updated': '-updated_at',  # За датою оновлення (найновіші спочатку)
#                 'title_asc': 'title',  # За заголовком (A-Z)
#                 'title_desc': '-title',  # За заголовком (Z-A)
#                 'popular': '-views',  # За переглядами (найбільше спочатку)
#                 'comments': '-comments_count'  # За кількістю коментарів
#             }
#
#             # Якщо параметр сортування коректний, застосовуємо його
#             if sort_by in sort_mapping:
#                 queryset = queryset.order_by(sort_mapping[sort_by])
#             else:
#                 # За замовчуванням - спочатку закріплені теми, потім за датою створення (найновіші спочатку)
#                 queryset = queryset.order_by('-is_pinned', '-created_at')
#         else:
#             # За замовчуванням - спочатку закріплені теми, потім за датою створення (найновіші спочатку)
#             queryset = queryset.order_by('-is_pinned', '-created_at')
#
#         return queryset
#
#
#     def perform_create(self, serializer):
#         try:
#             # Додаємо перевірку на наявність 'content' у request.data
#             content = self.request.data.get('content', '')
#             # Перевіряємо на наявність коду в контенті, але безпечно обробляємо різні типи даних
#             has_code = False
#             if content and isinstance(content, str):
#                 has_code = "```" in content
#             # Збереження запису з автоматичним призначенням автора
#             serializer.save(author=self.request.user, has_code=has_code)
#         except Exception as e:
#             # Додаємо логування для відстеження помилок
#             import traceback
#             print(f"ERROR creating forum topic: {str(e)}")
#             print(traceback.format_exc())
#             # Перекидаємо помилку далі, щоб Django міг обробити її належним чином
#             raise
#
# class ForumTopicDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ForumTopic.objects.all()
#     serializer_class = ForumTopicSerializer
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def get(self, request, *args, **kwargs):
#         topic = self.get_object()
#         # Збільшуємо лічильник переглядів
#         topic.views += 1
#         topic.save(update_fields=['views'])
#         return super().get(request, *args, **kwargs)
#
#     def update(self, request, *args, **kwargs):
#         topic = self.get_object()
#         # Перевіряємо права доступу
#         if topic.author != request.user and not request.user.is_staff:
#             return Response(
#                 {"detail": "У вас немає прав для редагування цієї теми."},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         return super().update(request, *args, **kwargs)
#
#     def destroy(self, request, *args, **kwargs):
#         topic = self.get_object()
#         # Перевіряємо права доступу
#         if topic.author != request.user and not request.user.is_staff:
#             return Response(
#                 {"detail": "У вас немає прав для видалення цієї теми."},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         return super().destroy(request, *args, **kwargs)
#
#
# class ForumCategoryListView(APIView):
#     permission_classes = [permissions.AllowAny]
#
#     def get(self, request):
#         # Отримуємо категорії з CATEGORY_CHOICES моделі ForumTopic
#         categories = [
#             {"id": choice[0], "name": choice[1]}
#             for choice in ForumTopic.CATEGORY_CHOICES
#         ]
#         return Response(categories)
#
#
# class ForumTopicLikeView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, pk):
#         try:
#             topic = ForumTopic.objects.get(pk=pk)
#             # Перевірка, чи користувач вже лайкнув цю тему
#             if request.user in topic.likes.all():
#                 return Response(
#                     {"detail": "Ви вже оцінили цю тему."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             # Додаємо користувача до тих, хто лайкнув
#             topic.likes.add(request.user)
#             return Response({"likes_count": topic.likes.count()})
#         except ForumTopic.DoesNotExist:
#             return Response(
#                 {"detail": "Тему не знайдено."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#
# class ForumTopicUnlikeView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, pk):
#         try:
#             topic = ForumTopic.objects.get(pk=pk)
#             # Перевірка, чи користувач лайкнув цю тему
#             if request.user not in topic.likes.all():
#                 return Response(
#                     {"detail": "Ви не оцінювали цю тему."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             # Видаляємо користувача з тих, хто лайкнув
#             topic.likes.remove(request.user)
#             return Response({"likes_count": topic.likes.count()})
#         except ForumTopic.DoesNotExist:
#             return Response(
#                 {"detail": "Тему не знайдено."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#
# class ForumTopicBookmarkView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, pk):
#         try:
#             topic = ForumTopic.objects.get(pk=pk)
#             # Перевірка, чи користувач вже додав цю тему в закладки
#             if request.user in topic.bookmarks.all():
#                 return Response(
#                     {"detail": "Ця тема вже у ваших закладках."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             # Додаємо тему в закладки користувача
#             topic.bookmarks.add(request.user)
#             return Response({"bookmarks_count": topic.bookmarks.count()})
#         except ForumTopic.DoesNotExist:
#             return Response(
#                 {"detail": "Тему не знайдено."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#
# class ForumTopicUnbookmarkView(APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, pk):
#         try:
#             topic = ForumTopic.objects.get(pk=pk)
#             # Перевірка, чи користувач додав цю тему в закладки
#             if request.user not in topic.bookmarks.all():
#                 return Response(
#                     {"detail": "Цієї теми немає у ваших закладках."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#             # Видаляємо тему з закладок користувача
#             topic.bookmarks.remove(request.user)
#             return Response({"bookmarks_count": topic.bookmarks.count()})
#         except ForumTopic.DoesNotExist:
#             return Response(
#                 {"detail": "Тему не знайдено."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#
#
# class UserBookmarksView(generics.ListAPIView):
#     serializer_class = ForumTopicSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_queryset(self):
#         # Отримуємо теми, які користувач додав у закладки
#         return ForumTopic.objects.filter(bookmarks=self.request.user).order_by('-created_at')