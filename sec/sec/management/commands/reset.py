from user.models import AccessAttempt
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        objects = AccessAttempt.objects.all()
        num = len(list(objects))
        objects.delete()
        print("Deleted {} records.".format(num))

    def add_arguments(self, parser):

        parser.add_argument(
            '--reset',
            help='Reset the login attempts for all IPs',
            default=1
        )