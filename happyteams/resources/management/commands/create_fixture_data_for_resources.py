from dateutil import parser
from pytz import timezone
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand, CommandError

try:
    import pandas as pd
except ImportError:
    pd = None

from planning.models import Month
from resources.models import Resource, OrganizationalUnit, ResourceRate


class Command(BaseCommand):
    help = 'Create fixture data for CRM app.'

    def handle(self, *args, **options):
        if settings.DEBUG:
            self.stdout.write(self.style.SUCCESS("Creating Fixture Data for HappyTeams Resources App"))
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

        if pd is None:
            self.style.ERROR("  - Need Pandas installed to process large excel spreadsheet")

        if hasattr(settings, 'FIXTURE_DATA_WORKBOOK'):
            rates = pd.read_excel(settings.FIXTURE_DATA_WORKBOOK,
                                  sheetname=getattr(settings, 'FIXTURE_DATA_WORKSHEET', 'Gov'), header=0)
        else:
            self.style.ERROR("  - Could not find 'FIXTURE_DATA_WORKBOOK' in settings.py, add it to local_settings.py")
            return

        self.stdout.write(self.style.SUCCESS("  Creating Fixture Data:"))

        self.stdout.write(self.style.SUCCESS("    - Creating Months"))
        months = {}
        for col in rates.columns:
            if isinstance(col, parser.datetime.datetime):
                months[col] = Month.objects.get(month=col.month, year=col.year)
            else:
                try:
                    date = parser.parse(col)
                    months[col] = Month.objects.get(month=date.month, year=date.year)
                except ValueError:
                    pass

        self.stdout.write(self.style.SUCCESS("    - Creating Resources and Organizational Units"))

        main_unit_name = getattr(settings, 'MAIN_UNIT', 'Organization')
        groups = {main_unit_name: Group(name=main_unit_name)}
        units = {main_unit_name: OrganizationalUnit(group=groups[main_unit_name])}
        users, resources, user_groups = {}, {}, {}
        resource_index = {}

        eastern_tz = timezone('US/Eastern')

        for i, name in enumerate(rates['Gov Rates - No Fee']):
            if isinstance(name, str) and ',' in name and rates[' Employee Number'][i] > 0:
                last, first = name.split(',', 1)
                first = first.strip().split(' ')
                middle_initial = ''
                if len(first) > 1:
                    middle_initial = first[1].strip()[0].upper()
                    first = first[0].strip()
                else:
                    first = first[0]
                last = last.strip()
                hire_date = rates[' Hire Date'][i]
                if isinstance(hire_date, str):
                    hire_date = parser.parse(hire_date)
                username = '{}{}{}'.format(first[0].lower(),
                                           last.lower(),
                                           User.objects.filter(last_name=last).count()+3)
                email = '{}.{}@{}'.format(first.lower(),
                                          last.lower(),
                                          getattr(settings, 'DEFAULT_EMAIL_DOMAIN', 'none.none'))
                users[username] = User(username=username,
                                       password=settings.DEFAULT_USER_PASSWORD,
                                       email=email,
                                       first_name=first,
                                       last_name=last,
                                       date_joined=eastern_tz.localize(hire_date),
                                       is_staff=False)

                resource_index[username] = i

                unit_name = ''
                parent_name = main_unit_name
                user_groups[username] = []
                for subunit_name in rates[' Org Unit'][i].split('-'):
                    parent_unit = units.get(parent_name)
                    unit_name += ('-' if unit_name else '') + subunit_name.strip()
                    if unit_name not in groups:
                        groups[unit_name] = Group(name=unit_name)
                        units[unit_name] = OrganizationalUnit(id=len(units) + 1,
                                                              group=groups[unit_name],
                                                              parent=parent_unit)
                    user_groups[username].append(unit_name)

                resources[username] = Resource(user=users[username],
                                               unit=units[unit_name],
                                               title=rates[' Job Title'][i],
                                               middle_initial=middle_initial,
                                               employee_number=rates[' Employee Number'][i])

        # Create Groups and Organizational Units
        Group.objects.bulk_create(groups.values())
        groups = {group.name: group for group in Group.objects.all()}
        for unit_name, unit in units.items():
            unit.group = groups[unit_name]
        OrganizationalUnit.objects.bulk_create(units.values())

        self.stdout.write(self.style.SUCCESS("    - Completed the Creation of Organizational Units"))

        # TODO: ask Danny if he knows of a less convoluted but equally fast way for bulk creating related models
        # Create Users and Resources
        User.objects.bulk_create(users.values())
        for user in User.objects.all():
            user.groups.add(*[groups[group_name] for group_name in user_groups.get(user.username, [])])
        User.objects.all().update()
        users = {user.username: user for user in User.objects.all()}
        units = {unit.group.name: unit for unit in OrganizationalUnit.objects.all()}
        for username, resource in resources.items():
            resource.user = users[username]
            resource.unit = units[resource.unit.group.name]
        Resource.objects.bulk_create(resources.values())
        resources = {resource.user.username: resource for resource in Resource.objects.all()}

        self.stdout.write(self.style.SUCCESS("    - Completed the Creation of Resources"))

        self.stdout.write(self.style.SUCCESS("    - Creating Employee Rates"))
        employee_rates = []
        for username, resource in resources.items():
            for col, month in months.items():
                rate = rates[col][resource_index[username]]
                if isinstance(rate, str):
                    rate = float(rate.replace('$', ''))
                employee_rates.append(ResourceRate(employee=resource,
                                                   month=month,
                                                   rate=rate))

        ResourceRate.objects.bulk_create(employee_rates)

        self.stdout.write(
            self.style.SUCCESS('  - Successfully created fixture data for HappyTeams Resources app')
        )
