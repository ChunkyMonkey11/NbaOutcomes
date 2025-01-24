from django.core.management.base import BaseCommand
# NEED TO COMMENT AND EXPLAIN THE FORMAT OF COMMAND
class Command(BaseCommand):
    help = "This is a custom management command example."

    def handle(self, *args, **kwargs):
        self.stdout.write("Hello! This is a custom command.")