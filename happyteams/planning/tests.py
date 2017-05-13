# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase

from crm.models import Project, Sponsor
from resources.models import Resource
from planning.models import Commitment


class TestCommitments(TestCase):
    def setUp(self):
        sponsor = Sponsor.objects.create(name='Flying Circus')

        self.project_a = Project.objects.create(name='Project A',
                                                sponsor=sponsor,
                                                start=date(2017, 7, 1),
                                                end=date(2018, 6, 30))
        self.project_b = Project.objects.create(name='Project B',
                                                sponsor=sponsor,
                                                start=date(2016, 1, 1),
                                                end=date(2020, 12, 31))

        self.resource_1 = Resource.objects.create(user=User.objects.create(username='test_user_1',
                                                                           password='password1',
                                                                           email='user1@example.org'))
        self.resource_2 = Resource.objects.create(user=User.objects.create(username='test_user_2',
                                                                           password='password2',
                                                                           email='user2@example.org'))

    def test_validations(self):
        with self.assertRaises(ValueError):
            Commitment.objects.create(project=self.project_a, resource=self.resource_1,
                                      start=date(2016, 1, 1), end=date(2016, 2, 1), hours=16.)
        with self.assertRaises(ValueError):
            Commitment.objects.create(project=self.project_a, resource=self.resource_1,
                                      start=date(2018, 1, 1), end=date(2018, 2, 1), hours=None, percentage=None)
        with self.assertRaises(ValueError):
            Commitment.objects.create(project=self.project_a, resource=self.resource_1,
                                      start=date(2018, 1, 1), end=date(2018, 2, 1), hours=40., percentage=40.)
        with self.assertRaises(ValueError):
            Commitment.objects.create(project=self.project_a, resource=self.resource_1,
                                      start=date(2018, 1, 1), end=date(2018, 2, 1), hours=200.)

    def test_hour_calculations(self):
        commitment_1 = Commitment.objects.create(project=self.project_a, resource=self.resource_1,
                                                 start=date(2017, 7, 1), end=date(2017, 7, 31), hours=40.)

        self.assertEqual(list(commitment_1.hours_per_month.values())[0], 40.)

        commitment_2 = Commitment.objects.create(project=self.project_a, resource=self.resource_1,
                                                 start=date(2017, 8, 15), end=date(2018, 6, 30), percentage=25.0)

        hours = commitment_2.hours_per_month
        self.assertEqual(len(hours), 11)
        self.assertEqual(hours[date(2017, 8, 1)], 26.)
        self.assertEqual(hours[date(2018, 2, 1)], 40.)
        self.assertEquals(commitment_2.hours_in_period(date(2017, 10, 5)),
                          {date(2017, 10, 1): 38.})

        commitment_3 = Commitment.objects.create(project=self.project_b, resource=self.resource_1,
                                                 start=self.project_b.start, end=self.project_b.end, hours=88.0)

        self.assertEquals(len(list(commitment_3.months)), 60)

        hours = commitment_3.hours_per_month

        self.assertEquals(hours[date(2020, 1, 1)], 88.)

        self.assertEquals(commitment_3.hours_in_period(date(2018, 1, 1)),
                          {date(2018, 1, 1): 88.})

        self.assertEquals(commitment_3.hours_in_period(date(2022, 1, 1)), {})
