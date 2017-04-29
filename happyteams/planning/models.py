# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date
from django.db import models
from calendar import Calendar, month_name, monthrange

from crm.models import Project
from resources.models import Resource


WORKWEEK_LENGTH = 5
WORK_HOURS_PER_DAY = 8
_calendar = Calendar()


class Month(models.Model):
    MONTHS = [(i, month_name[i]) for i in range(1, 13)]
    YEARS = [(i, i) for i in range(2015, 2026)]

    month = models.IntegerField(choices=MONTHS)
    year = models.IntegerField(choices=YEARS)
    work_hours = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (('month', 'year'),)

    def __init__(self, *args, **kwargs):
        super(Month, self).__init__(*args, **kwargs)
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
        for week in _calendar.monthdayscalendar(self.year, self.month):
            for i, day in enumerate(week):
                if day > 0 and i < WORKWEEK_LENGTH:
                    work_hours += WORK_HOURS_PER_DAY
        return work_hours


class Commitment(models.Model):
    """This model captures the commitments for a specific resource on a
    specific project.  The model is designed to allow for extended commitments
    of to allow for variation of commitments month to month.  Additionally, a
    commitment can be listed as a either a number of hours or a percentage.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    month = models.ForeignKey('Month')
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
