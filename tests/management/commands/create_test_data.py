from django.core.management.base import BaseCommand
from tests.models import Test

class Command(BaseCommand):
    help = 'Creates initial test data'

    def handle(self, *args, **kwargs):
        tests_data = [
            {
                'title': 'HTML',
                'icon': 'DiHtml5',
                'color': 'text-orange-500',
                'questions': 30,
                'duration': 60,
                'description': 'Основи HTML: теги, атрибути, семантика'
            },
            {
                'title': 'CSS',
                'icon': 'DiCss3',
                'color': 'text-blue-500',
                'questions': 30,
                'duration': 60,
                'description': 'Стилізація, Flexbox, Grid, анімації'
            },
            {
                'title': 'JavaScript',
                'icon': 'DiJsBadge',
                'color': 'text-yellow-400',
                'questions': 30,
                'duration': 60,
                'description': 'Основи JS, асинхронність, робота з DOM'
            },
            {
                'title': 'React',
                'icon': 'DiReact',
                'color': 'text-blue-400',
                'questions': 30,
                'duration': 60,
                'description': 'Компоненти, хуки, робота зі станом'
            },
            {
                'title': 'SQL',
                'icon': 'DiDatabase',
                'color': 'text-blue-600',
                'questions': 30,
                'duration': 60,
                'description': 'Запити, JOIN, індекси, оптимізація'
            },
            {
                'title': 'Django',
                'icon': 'DiDjango',
                'color': 'text-green-500',
                'questions': 30,
                'duration': 60,
                'description': 'Моделі, Views, шаблони, ORM'
            },
        ]

        for test_data in tests_data:
            Test.objects.update_or_create(
                title=test_data['title'],
                defaults=test_data
            )

        self.stdout.write(self.style.SUCCESS('Successfully created test data'))