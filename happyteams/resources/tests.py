# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase

from crm.models import Project
from planning.models import Commitment
from resources.models import Resource


class TestResource(TestCase):
    def setUp(self):
        project_a = Project.objects.create(name='Project A', start=date(2017, 7, 1), end=date(2018, 6, 30))
        project_b = Project.objects.create(name='Project B', start=date(2016, 1, 1), end=date(2020, 12, 31))

        self.resource_1 = Resource.objects.create(user=User.objects.create(username='test_user_1',
                                                                           password='password1',
                                                                           email='user1@example.org'))
        self.resource_2 = Resource.objects.create(user=User.objects.create(username='test_user_2',
                                                                           password='password2',
                                                                           email='user2@example.org'))

        Commitment.objects.create(project=project_a, resource=self.resource_1,
                                  start=date(2017, 7, 1), end=date(2017, 7, 31), hours=40)
        Commitment.objects.create(project=project_a, resource=self.resource_1,
                                  start=date(2017, 8, 1), end=date(2018, 6, 30), percentage=25.0)
        Commitment.objects.create(project=project_a, resource=self.resource_2,
                                  start=date(2017, 7, 1), end=date(2018, 6, 30), percentage=50.0)

        Commitment.objects.create(project=project_b, resource=self.resource_1,
                                  start=date(2016, 1, 1), end=date(2020, 12, 31), hours=10.)
        Commitment.objects.create(project=project_b, resource=self.resource_1,
                                  start=date(2017, 1, 1), end=date(2017, 12, 31), hours=70.)
        Commitment.objects.create(project=project_b, resource=self.resource_2,
                                  start=date(2016, 7, 15), end=date(2018, 12, 31), hours=40.)

    def test_coverage(self):
        pass

    def test_commitments(self):
        pass

    def test_enjoyment(self):
        pass
