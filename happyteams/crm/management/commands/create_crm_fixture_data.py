from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create fixture data for CRM app.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating Fixture Data for HappyTeams CRM App"))

        if settings.DEBUG and User.objects.filter(username=settings.FIXTURE_SUPER_USERNAME).count() == 0:
            self.stdout.write(self.style.SUCCESS("  Creating Superuser:"))
            User.objects.create_superuser(settings.FIXTURE_SUPER_USERNAME, 'admin@ers.gov',
                                          settings.FIXTURE_SUPER_PASSWORD)
            self.stdout.write(self.style.SUCCESS("    - Created superuser (username: '{}', password: '{}')")
                              .format(settings.FIXTURE_SUPER_USERNAME, settings.FIXTURE_SUPER_PASSWORD))

        self.stdout.write(
            self.style.SUCCESS('  - Successfully created fixture data for HappyTeams CRM app.')
        )
