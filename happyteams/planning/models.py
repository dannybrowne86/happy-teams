# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date
from django.db import models
from calendar import Calendar, month_name, monthrange

from crm.models import Project
from resources.models import Resource

_calendar = Calendar()


def starts(self):
    return datetime(self.year, self.month, 1)


def ends(month, year):
    return datetime(year, month, monthrange(year, month)[1], 23, 59, 59)


def calculate_work_hours(month, year, work_hrs_per_day=8, workweek_length=5):
    work_hours = 0
    for week in _calendar.monthdayscalendar(year, month):
        for i, day in enumerate(week):
            if day > 0 and i < workweek_length:
                work_hours += work_hrs_per_day
    return work_hours


class Commitment(models.Model):
    """This model captures the commitments for a specific resource on a
    specific project.  The model is designed to allow for extended commitments
    of to allow for variation of commitments month to month.  Additionally, a
    commitment can be listed as a either a number of hours or a percentage.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2,
                                     null=True, blank=True)
    hours = models.DecimalField(max_digits=7, decimal_places=2,
                                null=True, blank=True)

    def clean(self):
        # ensure that the 
        try:
            assert self.start >= self.project.start
            assert self.end > self.project.start
            assert self.start < self.project.end
            assert self.end <= self.project.end
        except:
            raise ValueError('Ensure the commitments dates are within the Project schedule.')
        
        if self.percentage is None and self.hours is None:
            raise ValueError('You must provide either a Percentage or Hours.')
        if self.percentage is not None and self.hours is not None:
            raise ValueError('You can provide either a Percentage or Hours, but not both.')

        if self.hours:
            # add logic to ensure the number of hours does not exceed the number
            # of working hours in the month.
            pass

    def save(self, *args, **kwargs):
        self.clean()
        return super(Commitment, self).save(*args, **kwargs)
