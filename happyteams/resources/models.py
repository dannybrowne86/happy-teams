# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import datetime


class OrganizationalUnit(models.Model):
    name = models.CharField(max_length=32)
    abbreviation = models.CharField(max_length=4)
    primary_manager = models.ForeignKey(User, null=True, blank=True,
                                        related_name='manages')
    secondary_manager = models.ForeignKey(User, null=True, blank=True,
                                          related_name='supports')
    parent = models.ForeignKey('self', null=True, blank=True)


class Resource(models.Model):
    user = models.OneToOneField(User)
    unit = models.ForeignKey(OrganizationalUnit)

    employee_number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=10)
    hire_date = models.DateField()

    def coverage(self, month=None):
        # calculate the coverage for the employee for the given month

        if month is None:
            month = datetime.date.today()
        return 1.0

    def enjoyment(self, month=None):
        # based on the resources assignments for the given month, what is
        # their level of enjoyment in their work?

        if month is None:
            month = datetime.date.today()
        return 3.0


class EmployeeRate(models.Model):
    employee = models.ForeignKey(Resource)
    month = models.ForeignKey('planning.Month')
    rate = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = (('employee', 'month'),)

    def __str__(self):
        return "{} {}: ${:.2f}/hr".format(self.employee, self.month, self.rate)


class Skill(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class SkillLevel(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    rank = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        unique_together = (('skill', 'rank',),)

    def save(self, *args, **kwargs):
        if (self.id is None and SkillLevel.
                objects.filter(skill=self.skill).count() >= 4):

            raise ValueError('You cannot have more than 4 levels for a skill.')

        return super(SkillLevel, self).save(*args, **kwargs)


class SkillEnjoyment(models.Model):
    slug = models.CharField(max_length=16)
    description = models.TextField()
    value = models.PositiveIntegerField()


class ResourceSkill(models.Model):
    """ This model captures how well a resource can execute a skill as well
    as their enjoyment level.
    """

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT)
    # can we limit the options here based on the ones
    skill_level = models.ForeignKey(SkillLevel, null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    help_text='How would you rate your abilities in this area?')
    enjoyment = models.ForeignKey(SkillEnjoyment, null=True, blank=True,
                                  on_delete=models.CASCADE,
                                  help_text='How much do you enjoying doing this type of work?')

    class Meta:
        unique_together = (('resource', 'skill',),)

    def clean(self):
        if self.skill_level:
            assert(self.skill == self.skill_level.skill)

    def save(self, *args, **kwargs):
        self.clean()
        return super(ResourceSkill, self).save(*args, **kwargs)
