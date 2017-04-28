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

    def coverage(self, month=datetime.date.today()):
        # calculate the coverage for the employee for the given month
        return 1.0

    def enjoyment(self, month=datetime.date.today()):
        # based on the resources assignments for the given month, what is
        # their level of enjoyment in their work?
        return 3.0


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
        if (self.id is None and
            SkillLevel.objects.filter(skill=self.skill).count() >= 4):

            raise 'You cannot have more than 4 levels for a skill.'

        return super(SkillLevel, self).save(*args, **kwargs)


class SkillEnjoyment(models.Model):
    # Populate the database with these values
    # NONE = 0
    # LITTLE = 1
    # ENJOY = 4
    # FAVORITE = 9
    # ENJOYMENT_LEVELS = (
    #     (NONE, 'Please don\'t make me do this.'),
    #     (LITTLE, 'Not my favorite but I\'ll do it if needed.'),
    #     (ENJOY, 'I enjoy doing this.')
    #     (FAVORITE, 'This is (one of) my favorite part(s) of my job.')
    # )
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
    skill_level = models.ForeignKey(SkillLevel,
        null=True, blank=True, on_delete=models.SET_NULL, 
        help_text='How would you rate your abilities in this area?')
    enjoyment = models.ForeignKey(SkillEnjoyment,
        null=True, blank=True, on_delete=models.CASCADE,
        help_text='How much do you enjoying doing this type of work?')


    class Meta:
        unique_together = (('resource', 'skill',),)

    def clean(self):
        if self.skill_level:
            assert(self.skill == self.skill_level.skill)

    def save(self, *args, **kwargs):
        self.clean()
        return super(ResourceSkill, self).save(*args, **kwargs)
