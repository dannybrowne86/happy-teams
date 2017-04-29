# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from collections import defaultdict
from datetime import date, datetime


# Create your models here.
class Sponsor(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)


class Deliverable(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True)
    primary_assignee = models.ForeignKey('resources.Resource', blank=True, null=True,
                                         related_name='owned_deliverables')
    supported_by = models.ManyToManyField('resources.Resource', blank=True, related_name='supported_deliverables')


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
    deliverables = models.ManyToManyField(Deliverable)

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


class BudgetIncrement(models.Model):
    start = models.DateField(
        help_text='What is the project\'s anticipated (or actual) start date?')
    end = models.DateField(
        help_text='What is the PoP of the funding? (expiration)')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    project = models.ForeignKey(Project)



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
    month = models.ForeignKey('planning.Month')
    # TODO: deconflict the monthly discretization of time with Danny's time ranges
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
