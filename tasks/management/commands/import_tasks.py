import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tests.models import Test
from tasks.models import InteractiveTask, TaskSolution


class Command(BaseCommand):
    help = 'Imports interactive tasks from JSON files to database'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to the JSON file with tasks')

    def handle(self, *args, **options):
        file_path = options.get('file')

        if file_path:
            if not os.path.exists(file_path):
                self.stdout.write(self.style.ERROR(f'File {file_path} not found'))
                return
            self._import_from_file(file_path)
            return

        data_dir = os.path.join(settings.BASE_DIR, '..', 'fronteder-interview-portal-backend', 'data', 'tests-tasks')

        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Directory {data_dir} not found'))
            data_dir = r'C:\Users\Ivan Kyrlan\Documents\Study\fronteder-interview-portal\fronteder-interview-portal-backend\data\tests-tasks'
            if not os.path.exists(data_dir):
                self.stdout.write(self.style.ERROR('No directory with tasks found'))
                return
            else:
                self.stdout.write(self.style.SUCCESS(f'Using alternative path: {data_dir}'))

        task_files = {
            'HTML': os.path.join('HTML', 'html-interactive-tasks.json'),
            'CSS': os.path.join('CSS', 'css-interactive-tasks.json'),
            'JavaScript': os.path.join('JavaScript', 'js-interactive-tasks.json'),
            'React': os.path.join('React', 'react-interactive-tasks.json'),
            'SQL': os.path.join('SQL', 'sql-interactive-tasks.json'),
            'Django': os.path.join('Django', 'django-interactive-tasks.json'),
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
                test_title = tasks_data.get('test_title', test_title)
                tasks = tasks_data.get('tasks', [])
            else:
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
                title = task_data.get('title')
                description = task_data.get('description')
                initial_code = task_data.get('initial_code')
                task_type = task_data.get('task_type', 'complete')

                if not all([title, description, initial_code]):
                    self.stdout.write(self.style.WARNING(f'Skipping task: missing required fields'))
                    continue

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

                solutions = task_data.get('solutions', [])
                if not solutions:
                    self.stdout.write(self.style.WARNING(f'No solutions provided for task "{title}"'))
                    continue

                task.solutions.all().delete()

                for idx, solution_data in enumerate(solutions):
                    if isinstance(solution_data, dict):
                        solution_code = solution_data.get('code')
                        is_primary = solution_data.get('is_primary', idx == 0)
                        hint = solution_data.get('hint')
                    else:
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