from django.core.management.base import BaseCommand
from django.contrib.admin.models import LogEntry

class Command(BaseCommand):
    help = 'Delete all admin log entries'

    def handle(self, *args, **kwargs):
        count, _ = LogEntry.objects.all().delete()
        self.stdout.write(f"Deleted {count} log entries.")
