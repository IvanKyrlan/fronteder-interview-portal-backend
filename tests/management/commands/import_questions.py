import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tests.models import Test, Question, Answer


class Command(BaseCommand):
    help = 'Imports questions from JSON files to database'

    def handle(self, *args, **kwargs):
        # Оновлений шлях до файлів на фронтенді
        data_dir = os.path.join(settings.BASE_DIR, '..', 'fronteder-interview-portal-frontend', 'src', 'data')

        # Перевіряємо, чи існує директорія
        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f'Directory {data_dir} not found'))
            # Спробуємо альтернативний шлях
            data_dir = r'C:\Users\Ivan Kyrlan\Documents\Study\fronteder-interview-portal\fronteder-interview-portal-backend\data'
            if not os.path.exists(data_dir):
                self.stdout.write(self.style.ERROR('No directory with questions found'))
                return
            else:
                self.stdout.write(self.style.SUCCESS(f'Using alternative path: {data_dir}'))

        question_files = {
            'HTML': os.path.join('HTML', 'html-interview-questions.json'),
            'CSS': os.path.join('CSS', 'css-interview-questions.json'),
            'JavaScript': os.path.join('JavaScript', 'js-interview-questions.json'),
            'React': os.path.join('React', 'react-interview-questions.json'),
            'SQL': os.path.join('SQL', 'sql-interview-questions.json'),
            'Django': os.path.join('Django', 'django-interview-questions.json'),
        }

        for test_title, filename in question_files.items():
            try:
                # Отримуємо тест
                test = Test.objects.get(title=test_title)

                # Читаємо файл
                file_path = os.path.join(data_dir, filename)
                if not os.path.exists(file_path):
                    self.stdout.write(self.style.WARNING(f'File {file_path} not found'))
                    continue

                with open(file_path, 'r', encoding='utf-8') as file:
                    questions_data = json.load(file)

                # Імпортуємо питання
                imported_count = 0
                for q_data in questions_data:
                    question_text = q_data.get('question', '').strip()

                    # Пропускаємо порожні питання
                    if not question_text:
                        self.stdout.write(self.style.WARNING(f'Skipping empty question in {filename}'))
                        continue

                    # Отримуємо відповіді
                    answers = q_data.get('answers', [])

                    # Переконуємося, що є рівно 4 непорожні відповіді
                    valid_answers = [ans for ans in answers if ans and ans.strip()]
                    if len(valid_answers) != 4:
                        self.stdout.write(self.style.WARNING(
                            f'Question "{question_text[:30]}..." has {len(valid_answers)} valid answers, expected 4. Skipping.'
                        ))
                        continue

                    # Перевіряємо індекс правильної відповіді
                    correct_answer_id = q_data.get('correctAnswerId')
                    if correct_answer_id is None or correct_answer_id < 0 or correct_answer_id >= len(valid_answers):
                        self.stdout.write(self.style.WARNING(
                            f'Question "{question_text[:30]}..." has invalid correctAnswerId. Setting first answer as correct.'
                        ))
                        correct_answer_id = 0

                    # Створюємо питання
                    question = Question.objects.create(
                        test=test,
                        question=question_text
                    )

                    # Створюємо відповіді
                    for idx, answer_text in enumerate(valid_answers):
                        Answer.objects.create(
                            question=question,
                            text=answer_text,
                            is_correct=(idx == correct_answer_id)
                        )

                    imported_count += 1

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {imported_count} questions for {test_title}'))

            except Test.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Test "{test_title}" not found in database'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing questions for {test_title}: {str(e)}'))