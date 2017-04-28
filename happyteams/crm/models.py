# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from calendar import Calendar, month_name, monthrange
from collections import defaultdict
from datetime import date, datetime


WORKWEEK_LENGTH = 5
WORK_HOURS_PER_DAY = 8
MONTHS = [(i, month_name[i]) for i in range(1, 13)]
YEARS = [(i, i) for i in range(2015, 2026)]
CALENDAR = Calendar()


# Create your models here.
class Sponsor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)


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
    sponsor = models.ForeignKey(Sponsor)
    predecessor = models.ForeignKey('self', blank=True, null=True,
        help_text='If this project is a follow-on from another project, '
                  'select that project here.')
    status = models.CharField(max_length=12, choices=STATUSES)
    start = models.DateField(
        help_text='What is the project\'s anticipated (or actual) start date?')
    end = models.DateField(
        help_text='What is the project\'s anticipated (or actual) end date?')

    def team_enjoyment(self, month=None):
        if month is None:
            month = date.today()
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


class Month(models.Model):
    month = models.IntegerField(choices=MONTHS)
    year = models.IntegerField(choices=YEARS)
    work_hours = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('month', 'year'),)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.work_hours is None:
            self.work_hours = self.calculate_work_hours()

    def __str__(self):
        return "{:02d}/{:4d}".format(self.month, self.year)

    @property
    def starts(self):
        return datetime(self.year, self.month, 1)

    @property
    def ends(self):
        return datetime(self.year, self.month, monthrange(self.year, self.month)[1], 23, 59, 59)

    def calculate_work_hours(self):
        work_hours = 0
        for week in CALENDAR.monthdayscalendar(self.year, self.month):
            for i, day in enumerate(week):
                if day > 0 and i < WORKWEEK_LENGTH:
                    work_hours += WORK_HOURS_PER_DAY
        return work_hours


class Account(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=16, primary_key=True)
    parent = models.ForeignKey('Account', blank=True, null=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return "{} (${:,.2f})".format(self.name, self.budget)

    @property
    def subaccounts(self):
        return Account.objects.filter(parent=self)

    @property
    def all_subaccounts(self):
        subaccounts = []
        for account in self.subaccounts:
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
    account = models.ForeignKey(Account)
    employee = models.ForeignKey('resources.Resource')
    month = models.ForeignKey(Month)
    planned = models.BooleanField(default=True)
    hours = models.DecimalField(max_digits=4, decimal_places=1)

    class Meta:
        unique_together = (('account', 'employee', 'month', 'planned'),)

    def __str__(self):
        return "{:.1f} hrs for {} on {} {}".format(self.hours,
                                                   self.employee.name,
                                                   self.month,
                                                   self.account.name)

    @property
    def cost(self):
        from resources.models import EmployeeRate
        return self.hours * EmployeeRate.objects.get(employee=self.employee,
                                                     month=self.month).rate
