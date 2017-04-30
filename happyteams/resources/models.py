# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from django.db import models
from django.contrib.auth.models import User, Group


class OrganizationalUnit(models.Model):
    group = models.OneToOneField(Group)
    name = models.CharField(max_length=64, blank=True)
    # TODO: investigate the value of treebeard or django-mptt to have better hierarchical models
    # parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    primary_manager = models.ForeignKey('Resource', null=True, blank=True,
                                        related_name='manages')
    secondary_manager = models.ForeignKey('Resource', null=True, blank=True,
                                          related_name='supports')

    def __init__(self, *args, **kwargs):
        # TODO: figure out a way to not ahave to replicate name, maybe use django-polymorphic?
        super(OrganizationalUnit, self).__init__(*args, **kwargs)
        if not self.name:
            self.name = self.group.name

    def __str__(self):
        return self.group.name

    class Meta:
        ordering = ['name']


class Resource(models.Model):
    user = models.OneToOneField(User)
    middle_initial = models.CharField(max_length=1)
    employee_number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=16)
    unit = models.ForeignKey(OrganizationalUnit, blank=True, null=True,
                             related_name='members')

    def __str__(self):
        if self.user.last_name and self.user.first_name:
            return "{}.{} {}".format(self.user.first_name[0].upper(),
                                     " {}.".format(self.middle_initial) if self.middle_initial else '',
                                     self.user.last_name)
        return self.user.username

    def coverage(self, month=None):
        # calculate the coverage for the employee for the given month
        month = month or date.today()
        return 1.0

    def enjoyment(self, month=None):
        # based on the resources assignments for the given month, what is
        # their level of enjoyment in their work?
        month = month or date.today()
        return 3.0


class ResourceRate(models.Model):
    employee = models.ForeignKey(Resource, related_name='rates')
    start = models.DateField(help_text="The date the rate starts, future rates will supersede it")
    rate = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ('employee', 'start')

    def __str__(self):
        return "{} {:%b-%Y}: ${:.2f}/hr".format(self.employee, self.start, self.rate)


class Skill(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class SkillLevel(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT,
                              related_name='levels')
    rank = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        unique_together = ('skill', 'rank')

    def save(self, *args, **kwargs):
        if (self.id is None and SkillLevel.
                objects.filter(skill=self.skill).count() >= 4):

            raise ValueError('You cannot have more than 4 levels for a skill.')

        return super(SkillLevel, self).save(*args, **kwargs)

    def __str__(self):
        return "{}={}".format(self.skill.name, self.rank)


class SkillEnjoyment(models.Model):
    slug = models.CharField(max_length=16)
    description = models.TextField()
    value = models.PositiveIntegerField()

    def __str__(self):
        return self.slug


class ResourceSkill(models.Model):
    """
    This model captures how well a resource can execute a skill as well as their enjoyment level.

    """

    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name='resources')
    skill_level = models.ForeignKey(SkillLevel, null=True, blank=True,
                                    on_delete=models.SET_NULL,
                                    help_text='How would you rate your abilities in this area?')
    enjoyment = models.ForeignKey(SkillEnjoyment, null=True, blank=True,
                                  on_delete=models.CASCADE,
                                  help_text='How much do you enjoying doing this type of work?')

    class Meta:
        unique_together = ('resource', 'skill')

    def clean(self):
        if self.skill_level:
            assert(self.skill == self.skill_level.skill)

    def save(self, *args, **kwargs):
        self.clean()
        return super(ResourceSkill, self).save(*args, **kwargs)

    def __str__(self):
        return "<{}> {} {}".format(self.resource, self.enjoyment, self.skill_level)
