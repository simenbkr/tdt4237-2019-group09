from user.models import AccessAttempt
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        if options['reset']:
            objects = AccessAttempt.objects.all()
            num = len(list(objects))
            objects.delete()
            print("Deleted {} records.".format(num))

        elif options['list']:
            objects = AccessAttempt.objects.all()
            out = ''
            for object in objects:
                out += "{} | {} | {} | {} | {}".format(object.ip_addr, object.username, object.attempt_time,
                                                       object.user_agent, object.login_valid)

            print(out)

    def add_arguments(self, parser):

        parser.add_argument(
            '--reset',
            help='Reset the login attempts for all IPs',
            default=1
        )

        parser.add_argument(
            '--list',
            help='List login attempts.',
            default=1
        )