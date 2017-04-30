from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from random import choice

from planning.models import ends
from crm.models import BudgetIncrement, Project, Sponsor


class Command(BaseCommand):
    help = 'Create fixture data for CRM app.'

    def handle(self, *args, **options):
        if settings.DEBUG:
            self.stdout.write(self.style.SUCCESS("Creating Fixture Data for HappyTeams CRM App"))
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

        sponsors = {
            'Graham Chapman': 'Arthur, King of the Britons',
            'John Cleese': 'Sir Lancelot the Brave',
            'Terry Gilliam': 'Patsy',
            'Eric Idle': 'Sir Robin the Not-Quite-So-Brave-as-Sir-Lancelot',
            'Terry Jones': 'Sir Bedevere the Wise',
            'Michael Palin': 'Sir Galahad the Pure',
        }
        sponsors = [Sponsor(name=k, description=v) for k, v in sponsors.items()]
        Sponsor.objects.bulk_create(sponsors)
        sponsors = list(Sponsor.objects.all())

        projects = {
            'Project #1': {
                'budget': 250000.,
                'contract_number': '#F144023-5125-B1244A',
                'start': '12/2016',
                'end': '06/2017',
            },
            'Project #2': {
                'budget': 325000.,
                'contract_number': '#F144023-5125-A12345',
                'start': '11/2016',
                'end': '06/2018',
            },
            'Project #3': {
                'budget': 1325000.,
                'contract_number': '#F51355-4512545545-12',
                'start': '11/2016',
                'end': '12/2020',
            },
        }

        for name, data in projects.items():
            month, year = map(int, data.pop('start').split('/'))
            start = date(year=year, month=month, day=1)
            month, year = map(int, data.pop('end').split('/'))
            end = ends(year=year, month=month)
            budget = data.pop('budget', 0.0)
            project = Project.objects.create(name=name,
                                             start=start,
                                             end=end,
                                             sponsor=choice(sponsors),
                                             **data)
            BudgetIncrement.objects.create(project=project, amount=budget,
                                           start=start, end=end)

        self.stdout.write(
            self.style.SUCCESS('  - Successfully created fixture data for HappyTeams CRM app')
        )
