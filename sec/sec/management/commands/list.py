from user.models import AccessAttempt
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        objects = AccessAttempt.objects.all()
        out = ''
        for object in objects:
            out += "{} | {} | {} | {} | {}".format(object.ip_addr, object.username, object.attempt_time,
                                                       object.user_agent, object.login_valid)
            out += "\n"
            out += "="*100
            out += "\n"

        print(out)
        print("{} records shown.".format(len(list(objects))))

    def add_arguments(self, parser):

        parser.add_argument(
            '--list',
            help='List login attempts.',
            default=1
        )