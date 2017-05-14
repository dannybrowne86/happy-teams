# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase

from crm.models import Project, Sponsor
from planning.models import Commitment
from resources.models import Resource


class TestResource(TestCase):
    def setUp(self):
        sponsor = Sponsor.objects.create(name='Flying Circus')
        project_a = Project.objects.create(name='Project A',
                                           sponsor=sponsor,
                                           start=date(2017, 7, 1),
                                           end=date(2018, 6, 30))
        project_b = Project.objects.create(name='Project B',
                                           sponsor=sponsor,
                                           start=date(2016, 1, 1),
                                           end=date(2020, 12, 31))

        self.resource_1 = Resource.objects.create(user=User.objects.create(first_name='Ron',
                                                                           last_name='Obvious',
                                                                           username='test_user_1',
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

    def test_representation(self):
        self.assertIn('Obvious', str(self.resource_1))
        self.assertEquals('test_user_2', str(self.resource_2))

    def test_coverage(self):
        coverage = self.resource_2.coverage
        self.assertAlmostEquals(coverage[date(2018, 9, 1)], 0.25)

        coverage = self.resource_2.coverage_in_period(start=date(2017, 7, 1), end=date(2017, 9, 5))
        self.assertAlmostEquals(coverage[date(2017, 7, 1)], 0.5 + (40 / (21 * 8)))

        coverage = self.resource_2.coverage_in_period(start=date(2017, 7, 1), end=date(2017, 9, 5))
        self.assertAlmostEquals(coverage[date(2017, 8, 1)], 0.5 + 40 / (23 * 8))

    def test_commitments(self):
        hours = self.resource_1.committed_hours
        self.assertEquals(len(hours), 60)
        self.assertEquals(hours[date(2017, 7, 1)], 120.)
        self.assertEquals(hours[date(2020, 9, 1)], 10.)
        self.assertNotIn(date(2021, 1, 1), hours)

        hours = self.resource_2.committed_hours_in_period(start=date(2016, 1, 1))
        self.assertEquals(hours, {})

        hours = self.resource_1.committed_hours_in_period(start=date(2017, 7, 1), end=date(2017, 9, 15))
        self.assertEquals(hours[date(2017, 8, 1)], 70 + 10 + 0.25 * 184)

    def test_enjoyment(self):
        pass
