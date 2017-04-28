# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import datetime

# Create your models here.
class Sponsor(models.Model):
    name = models.CharField(max_length=65, unique=True)
    description = models.TextField(blank=True)


class Project(models.Model):
    STATUSES = (
        ('opportunity', 'Opportunity'), # low probability project
        ('pending', 'Pending'), # high probability project (90%)
        ('active', 'Active'), # project active
        ('close-out', 'Close Out'), # in close-out plan, committments firm
        ('archived', 'Archived') # project closed
    )

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    sponsor = models.ForeignKey(Sponsor)
    predecessor = models.ForeignKey('self', blank=True, null=True,
        help_text='If this project is a follow-on from another project, '
                  'select that project here.')
    status = models.CharField(max_length=12, choices=STATUSES)
    start = models.DateField(
        help_text='What is the project\'s anticipated (or actual) start date?')
    end = models.DateField(
        help_text='What is the project\'s anticipated (or actual) end date?')

    def team_enjoyment(self, month=datetime.date.today()):
        # based on the team member assignments, what is the overall team's
        # level of enjoyment with the project?
        return 1.0


class BudgetIncrement(models.Model):
    start = models.DateField(
        help_text='What is the project\'s anticipated (or actual) start date?')
    end = models.DateField(
        help_text='What is the PoP of the funding? (expiration)')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    project = models.ForeignKey(Project)

