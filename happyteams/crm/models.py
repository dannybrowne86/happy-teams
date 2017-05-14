# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import defaultdict
from datetime import date, datetime
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .util import get_month_start_dates, get_last_day_of_the_month


@python_2_unicode_compatible
class Sponsor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return "<Sponsor: {}>".format(self.name)


@python_2_unicode_compatible
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


@python_2_unicode_compatible
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


@python_2_unicode_compatible
class Task(models.Model):
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    project = models.ForeignKey(Project, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        if self.project is None:
            self.project = self.parent.project


@python_2_unicode_compatible
class BudgetIncrement(models.Model):
    project = models.ForeignKey(Project, related_name='budget_increments')
    task = models.ForeignKey(Task, blank=True, null=True, related_name='budget_increments')
    start = models.DateField(
        help_text="What is the project's anticipated (or actual) start date?")
    end = models.DateField(
        help_text="What is the PoP of the funding? (expiration)")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    comments = models.TextField(blank=True)


@python_2_unicode_compatible
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


@python_2_unicode_compatible
class Charge(models.Model):
    account = models.ForeignKey(Account, related_name='charges')
    employee = models.ForeignKey('resources.Resource', related_name='charges')
    start = models.DateField(help_text="Start date for the charge")
    end = models.DateField(blank=True, null=True, help_text="End date for the charge")
    hours = models.DecimalField(max_digits=4, decimal_places=1)

    def __init__(self, *args, **kwargs):
        super(Charge, self).__init__(*args, **kwargs)
        if self.end is None:
            self.end = get_last_day_of_the_month(self.start)

    def __str__(self):
        return "{:.1f} hrs for {} on {:2d}/{:4d} {}".format(self.hours,
                                                            self.employee.name,
                                                            self.start.month,
                                                            self.start.date,
                                                            self.account.name)

    @property
    def months(self):
        """Generates the start date for the months in the commitment period."""
        assert self.start < self.end, "Must end after start (start: {}, end: {})".format(self.start, self.end)
        for month in get_month_start_dates(start=self.start, end=self.end):
            yield month

    @property
    def cost(self):
        if self.end.month > self.start.month:
            raise NotImplementedError("Need to calculate multi-month charges")
        return self.hours * self.employee.rates.filter(start__lte=self.start).latest('start')
