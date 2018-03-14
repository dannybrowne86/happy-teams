from django.core.management.base import BaseCommand
from resources.models import SkillEnjoyment


class Command(BaseCommand):
    help = ('Populates the database with a suggested set of '
            'Skill Enjoyment Levels.')

    def handle(self, *args, **options):
        enjoyment_levels = [
            ('None', 0, "Please don't make me do this."),
            ('Little', 1, "Not my favorite but I'll do it if needed."),
            ('Enjoy', 4, "I enjoy doing this."),
            ('Favorite', 9, "This is (one of) my favorite part(s) of my job."),
        ]

        for enjoyment_level in enjoyment_levels:
            SkillEnjoyment.objects.create(
                slug=enjoyment_level[0],
                value=enjoyment_level[1],
                description=enjoyment_level[2]
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully loaded Skill Levels')
        )
