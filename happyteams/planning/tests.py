# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase

from crm.models import Project
from resources.models import Resource
from planning.models import Commitment


class TestCommitments(TestCase):
    def setUp(self):
        self.project_a = Project.objects.create(name='Project A',
                                                start=date(2017, 7, 1),
                                                end=date(2018, 6, 30))
        self.project_b = Project.objects.create(name='Project B',
                                                start=date(2016, 1, 1),
                                                end=date(2020, 12, 31))

        self.resource_1 = Resource.objects.create(user=User.objects.create(username='test_user_1',
                                                                           password='password1',
                                                                           email='user1@example.org'))
        self.resource_2 = Resource.objects.create(user=User.objects.create(username='test_user_2',
                                                                           password='password2',
                                                                           email='user2@example.org'))

    def test_hour_calculations(self):
        Commitment.objects.create()
