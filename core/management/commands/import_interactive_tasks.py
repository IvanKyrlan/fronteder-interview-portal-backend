# core/management/commands/import_interactive_tasks.py

import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Test, InteractiveTask, TaskSolution


class Command(BaseCommand):
    help = 'Imports interactive tasks from JSON files to database'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the JSON file with tasks')

    def handle(self, *args, **options):
        file_path = options.get('file')

        if file_path:
            # Використовуємо шлях вказаний користувачем
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f'File {file_path} not found'))
                return
            self._import_from_file(file_path)
            return

        # Якщо шлях не вказаний, шукаємо у стандартних місцях
        data_dir = os.path.join(settings.BASE_DIR, '..', 'frontend', 'project-frontender-quiz', 'src', 'data')

        # Перевіряємо, чи існує директорія
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Directory {data_dir} not found'))
            # Спробуємо альтернативний шлях
            data_dir = r'C:\Users\Ivan Kyrlan\Documents\Study\Graduation Project\frontender-quiz\frontend\project-frontender-quiz\src\data'
            if not os.path.exists(data_dir):
                self.stdout.write(self.style.ERROR('No directory with tasks found'))
                return
            else:
                self.stdout.write(self.style.SUCCESS(f'Using alternative path: {data_dir}'))

        task_files = {
            'JavaScript': 'js-interactive-tasks.json',
            'React': 'react-interactive-tasks.json',
            'HTML5': 'html-interactive-tasks.json',
            'CSS3': 'css-interactive-tasks.json',
            'Django': 'django-interactive-tasks.json',
        }

        for test_title, filename in task_files.items():
            file_path = os.path.join(data_dir, filename)
            if os.path.exists(file_path):
                self._import_from_file(file_path, test_title)
            else:
                self.stdout.write(self.style.WARNING(f'File {filename} not found'))

    def _import_from_file(self, file_path, test_title=None):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tasks_data = json.load(file)

            if not isinstance(tasks_data, dict) and not isinstance(tasks_data, list):
                self.stdout.write(self.style.ERROR(f'Invalid JSON format in {file_path}'))
                return

            if isinstance(tasks_data, dict):
                # Формат: {"test_title": "JavaScript", "tasks": [...]}
                test_title = tasks_data.get('test_title', test_title)
                tasks = tasks_data.get('tasks', [])
            else:
                # Формат: [{"test_title": "JavaScript", "title": "Task 1", ...}, ...]
                tasks = tasks_data
                if not test_title and tasks and 'test_title' in tasks[0]:
                    test_title = tasks[0]['test_title']

            if not test_title:
                self.stdout.write(self.style.ERROR(f'Test title not specified for {file_path}'))
                return

            try:
                test = Test.objects.get(title=test_title)
            except Test.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Test with title "{test_title}" not found in database'))
                return

            imported_count = 0
            for task_data in tasks:
                # Обов'язкові поля
                title = task_data.get('title')
                description = task_data.get('description')
                initial_code = task_data.get('initial_code')
                task_type = task_data.get('task_type', 'complete')

                # Перевірка обов'язкових полів
                if not all([title, description, initial_code]):
                    self.stdout.write(self.style.WARNING(f'Skipping task: missing required fields'))
                    continue

                # Створюємо або оновлюємо завдання
                task, created = InteractiveTask.objects.update_or_create(
                    test=test,
                    title=title,
                    defaults={
                        'description': description,
                        'initial_code': initial_code,
                        'task_type': task_type,
                        'difficulty': task_data.get('difficulty', 1)
                    }
                )

                # Додаємо рішення
                solutions = task_data.get('solutions', [])
                if not solutions:
                    self.stdout.write(self.style.WARNING(f'No solutions provided for task "{title}"'))
                    continue

                # Видаляємо наявні рішення перед додаванням нових
                task.solutions.all().delete()

                for idx, solution_data in enumerate(solutions):
                    if isinstance(solution_data, dict):
                        solution_code = solution_data.get('code')
                        is_primary = solution_data.get('is_primary', idx == 0)
                        hint = solution_data.get('hint')
                    else:
                        # Якщо рішення передане як рядок
                        solution_code = solution_data
                        is_primary = (idx == 0)
                        hint = None

                    if solution_code:
                        TaskSolution.objects.create(
                            task=task,
                            solution_code=solution_code,
                            is_primary=is_primary,
                            hint=hint
                        )

                imported_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'Successfully imported {imported_count} interactive tasks for {test_title}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing tasks: {str(e)}'))