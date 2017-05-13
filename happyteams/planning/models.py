# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from logging import getLogger

from crm.models import Project, Account
from crm.util import calculate_work_hours, get_first_day_of_the_month, get_month_start_dates, get_last_day_of_the_month
from resources.models import Resource

logger = getLogger(__name__)


class Commitment(models.Model):
    """This model captures the commitments for a specific resource on a
    specific project.  The model is designed to allow for extended commitments
    of to allow for variation of commitments month to month.  Additionally, a
    commitment can be listed as a either a number of hours or a percentage.
    """

    project = models.ForeignKey(Project, on_delete=models.CASCADE,
                                related_name='commitments')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE,
                                 related_name='commitments')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True,
                                related_name='commitments')
    start = models.DateField(help_text="The date on which the commitment is expected to commence.")
    end = models.DateField(help_text="The date on which the commitment is expected to terminate.")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                     validators=[MinValueValidator(0.), MaxValueValidator(100.)],
                                     help_text="The percent of time committed by this resource.")
    hours = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True,
                                help_text="The hours per month committed by this resource throughout the period.")

    def clean(self):
        try:
            assert self.start >= self.project.start
            assert self.end > self.project.start
            assert self.start < self.project.end
            assert self.end <= self.project.end
        except AssertionError:
            raise ValueError('Ensure the commitments dates are within the Project schedule.')
        
        if self.percentage is None and self.hours is None:
            raise ValueError('You must provide either a Percentage or Hours.')
        if self.percentage is not None and self.hours is not None:
            raise ValueError('You can provide either a Percentage or Hours, but not both.')

        if self.hours:
            for month in get_month_start_dates(start=self.start, end=self.end):
                start_day = max(self.start, get_first_day_of_the_month(month))
                end_day = min(get_last_day_of_the_month(month), self.end)

                if self.hours > calculate_work_hours(year=month.year, month=month.month,
                                                     start_day=start_day, end_day=end_day):
                    msg = '{} hrs exceeds working hours for the month of {}/{}'
                    raise ValueError(msg.format(self.hours, month.month, month.year))

    @property
    def months(self):
        """Generates the start date for the months in the commitment period."""
        for month in get_month_start_dates(start=self.start, end=self.end):
            yield month

    @property
    def hours_per_month(self):
        return self.hours_in_period(self.start, self.end)

    def hours_in_period(self, start, end=None):
        use_percentage = self.percentage is not None

        if end is None:
            end = get_last_day_of_the_month(start)

        if end < self.start or start > self.end:
            return {}

        end = min(end, self.end)
        start_day = self.start.day if self.start > start else start.day

        # If only asking for one month, return a single number
        if start.year == end.year and start.month == end.month:
            month = get_first_day_of_the_month(start)
            end_day = self.end.day if self.end < end else end.day
            if use_percentage:
                return {month: calculate_work_hours(year=start.year,
                                                    month=start.month,
                                                    start_day=start_day,
                                                    end_day=end_day) * 0.01 * float(self.percentage)}
            else:
                return {month: self.hours}

        result = {}
        for month in get_month_start_dates(start=start, end=end):
            hours = calculate_work_hours(year=month.year,
                                         month=month.month,
                                         start_day=month.day,
                                         end_day=self.end.day if self.end < get_last_day_of_the_month(month) else 31)
            if month.day > 1:
                month = get_first_day_of_the_month(month)
            if use_percentage:
                result[month] = hours * 0.01 * float(self.percentage)
            else:
                result[month] = self.hours
        return result

    def save(self, *args, **kwargs):
        self.clean()
        return super(Commitment, self).save(*args, **kwargs)
