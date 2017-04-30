# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from calendar import Calendar, monthrange
from collections import defaultdict
from datetime import date, datetime
from django.db import models


_calendar = Calendar()


def month_starts(month, year):
    return datetime(year, month, 1)


def month_ends(month, year):
    return datetime(year, month, monthrange(year, month)[1], 23, 59, 59, 99999)


def calculate_work_hours(month, year, work_hrs_per_day=8, workweek_starts=0, workweek_ends=5):
    work_hours = 0
    for week in _calendar.monthdayscalendar(year, month):
        for i, day in enumerate(week):
            if day > workweek_starts and i < workweek_ends:
                work_hours += work_hrs_per_day
    return work_hours


class Sponsor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return "<Sponsor: {}>".format(self.name)


class Deliverable(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    primary_assignee = models.ForeignKey('resources.Resource', blank=True, null=True,
                                         related_name='owned_deliverables')
    supported_by = models.ManyToManyField('resources.Resource', blank=True,
                                          related_name='supported_deliverables')

    def __str__(self):
        return self.name


class Project(models.Model):
    STATUSES = (
        ('opportunity', 'Opportunity'),  # low probability project
        ('pending', 'Pending'),  # high probability project (90%)
        ('active', 'Active'),  # project active
        ('close-out', 'Close Out'),  # in close-out plan, commitments firm
        ('archived', 'Archived')  # project closed
    )

    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    contract_number = models.CharField(max_length=32, blank=True)
    sponsor = models.ForeignKey(Sponsor)
    predecessor = models.ForeignKey('self', blank=True, null=True,
                                    help_text='If this project is a follow-on from another project, ' +
                                              'select that project here.')
    status = models.CharField(max_length=12, choices=STATUSES, default='opportunity')
    start = models.DateField(blank=True, null=True,
                             help_text="What is the project's anticipated (or actual) start date?")
    end = models.DateField(blank=True, null=True,
                           help_text="What is the project's anticipated (or actual) end date?")
    deliverables = models.ManyToManyField(Deliverable, blank=True, related_name='projects')

    def team_enjoyment(self, month=None):
        if month is None:
            month = date.today()
        # based on the team member assignments, what is the overall team's
        # level of enjoyment with the project?
        return 1.0

    @property
    def subaccounts(self):
        return Account.objects.filter(project=self)

    @property
    def charges(self):
        charges = defaultdict(dict)
        for account in self.subaccounts:
            charges[account] = account.direct_charges
        return charges

    def __str__(self):
        return self.name


class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    project = models.ForeignKey(Project, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        if self.project is None:
            self.project = self.parent.project


class BudgetIncrement(models.Model):
    start = models.DateField(
        help_text='What is the project\'s anticipated (or actual) start date?')
    end = models.DateField(
        help_text='What is the PoP of the funding? (expiration)')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    project = models.ForeignKey(Project)


class Account(models.Model):
    project = models.ForeignKey(Project, blank=True, null=True, related_name='accounts')
    name = models.CharField(max_length=16, primary_key=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

        if self.project is None and self.parent:
            self.project = self.parent.project

    def __str__(self):
        return "{}{} (${:,.2f})".format('{}.'.format(self.parent.name) if self.parent else '',
                                        self.name,
                                        self.budget or 0.)

    @property
    def subaccounts(self):
        return Account.objects.filter(parent=self)

    @property
    def all_subaccounts(self):
        subaccounts = []
        for account in self.subaccounts.all():
            subaccounts += [account] + account.all_subaccounts
        return subaccounts

    @property
    def direct_charges(self):
        now = datetime.now()
        charges = defaultdict(lambda: defaultdict(float))
        for charge in Charge.objects.filter(account=self):
            ends = charge.month.ends
            if (charge.planned and ends > now) or (not charge.planned and ends < now):
                charges[charge.employee][charge.month] = charge.cost
        return charges

    @property
    def all_charges(self):
        charges = self.direct_charges
        for account in self.all_subaccounts:
            for employee, monthly_charge in account.all_charges.items():
                for month, charge in monthly_charge.items():
                    charges[employee][month] += float(charge)
        return charges


class Charge(models.Model):
    account = models.ForeignKey(Account, related_name='charges')
    employee = models.ForeignKey('resources.Resource', related_name='charges')
    start = models.DateField(help_text="Start date for the charge")
    end = models.DateField(blank=True, null=True, help_text="End date for the charge")
    hours = models.DecimalField(max_digits=4, decimal_places=1)

    def __init__(self, *args, **kwargs):
        super(Charge, self).__init__(*args, **kwargs)
        if self.end is None:
            self.end = month_ends(month=self.start.month, year=self.start.year)

    def __str__(self):
        return "{:.1f} hrs for {} on {:2d}/{:4d} {}".format(self.hours,
                                                            self.employee.name,
                                                            self.start.month,
                                                            self.start.date,
                                                            self.account.name)

    @property
    def cost(self):
        return self.hours * self.employee.rates.filter(start__range=self.start)
