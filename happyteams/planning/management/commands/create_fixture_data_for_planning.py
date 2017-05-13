from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create fixture data for CRM app.'

    def handle(self, *args, **options):
        if settings.DEBUG:
            self.stdout.write(self.style.SUCCESS("Creating Fixture Data for HappyTeams Planning App"))
        else:
            self.stdout.write(self.style.ERROR("Must be in DEBUG mode to create fixture data"))
            return

        if User.objects.filter(username=settings.FIXTURE_SUPER_USERNAME).count() == 0:
            self.stdout.write(self.style.SUCCESS("  Creating Superuser:"))
            User.objects.create_superuser(settings.FIXTURE_SUPER_USERNAME, 'admin@happyteams.gtri.gatech.edu',
                                          settings.FIXTURE_SUPER_PASSWORD)
            self.stdout.write(self.style.SUCCESS("    - Created superuser (username: '{}', password: '{}')")
                              .format(settings.FIXTURE_SUPER_USERNAME, settings.FIXTURE_SUPER_PASSWORD))
        else:
            self.stdout.write(self.style.SUCCESS("    - Superuser (username: '{}') already created"))

        self.stdout.write(self.style.SUCCESS("  Creating Fixture Data:"))

        # TODO: add fixture data here (when we have a better model for commitments)

        self.stdout.write(
            self.style.SUCCESS('  - Successfully created fixture data for HappyTeams Planning app')
        )