from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create an admin user automatically'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')
            self.stdout.write(self.style.SUCCESS('Admin created!'))
        else:
            self.stdout.write(self.style.WARNING('Admin already exists!'))
