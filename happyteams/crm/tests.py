# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from datetime import date, datetime
from django.test import TestCase

from .util import (get_first_day_of_the_month, get_last_day_of_the_month, get_month_end_time, get_month_start_dates,
                   get_month_start_time, calculate_work_hours_in_month)


class TestDateUtils(TestCase):
    def setUp(self):
        pass

    def test_get_first_day_of_the_month(self):
        result = get_first_day_of_the_month()
        today = date.today()
        self.assertEquals(result.day, 1)
        self.assertEquals(result.month, today.month)
        self.assertEquals(result.year, today.year)

        result = get_first_day_of_the_month('2017/10')
        self.assertEquals(result.day, 1)
        self.assertEquals(result.month, 10)
        self.assertEquals(result.year, 2017)

        result = get_first_day_of_the_month(month=12)
        self.assertEquals(result, date(today.year, 12, 1))

        result = get_first_day_of_the_month(year=2018)
        self.assertEquals(result, date(2018, today.month, 1))

    def test_get_month_start_time(self):
        result = get_month_start_time('15/2/2020')
        self.assertEquals(result.year, 2020)
        self.assertEquals(result.month, 2)
        self.assertEquals(result.day, 1)
        self.assertEquals(result.hour, 0)
        self.assertEquals(result.minute, 0)

        result = get_month_start_time(date(2019, 1, 28))
        self.assertEquals(result.year, 2019)
        self.assertEquals(result.month, 1)
        self.assertEquals(result.day, 1)
        self.assertEquals(result.hour, 0)
        self.assertEquals(result.minute, 0)

    def test_get_last_day_of_the_month(self):
        result = get_last_day_of_the_month(date(2020, 2, 15))
        self.assertEquals(result.year, 2020)
        self.assertEquals(result.month, 2)
        self.assertEquals(result.day, 29)

        result = get_last_day_of_the_month('2/1/2024')
        self.assertEquals(result.year, 2024)
        self.assertEquals(result.month, 2)
        self.assertEquals(result.day, 29)

    def test_get_month_end_time(self):
        result = get_month_end_time('1/1/2017')
        self.assertGreater(result, datetime(2017, 1, 1, 23, 59))

        result = get_month_end_time(date(2024, 2, 5))
        self.assertGreater(result, datetime(2024, 2, 29, 23, 59))
        self.assertLess(result, datetime(2024, 3, 1))

    def test_get_month_start_dates(self):
        result = get_month_start_dates(date(2017, 5, 15), date(2017, 7, 29))
        self.assertIn(date(2017, 5, 15), result)
        self.assertIn(date(2017, 6, 1), result)
        self.assertIn(date(2017, 7, 1), result)

    def test_calculate_work_hours_in_month(self):
        self.assertEquals(calculate_work_hours_in_month(year=2017, month=5), 23 * 8)

        self.assertEquals(calculate_work_hours_in_month(year=2020, month=2, start_day=1), 20 * 8)
        self.assertEquals(calculate_work_hours_in_month(year=2020, month=2, start_day=5), 18 * 8)
        self.assertEquals(calculate_work_hours_in_month(year=2020, month=2, start_day=1, end_day=2), 0 * 8)
        self.assertEquals(calculate_work_hours_in_month(year=2020, month=2, start_day=5, end_day=6), 2 * 8)
        self.assertEquals(calculate_work_hours_in_month(year=2020, month=2, start_day=1, end_day=15), 10 * 8)

        self.assertEquals(calculate_work_hours_in_month(year=2020, month=2, work_hrs_per_day=10), 20 * 10)
        self.assertEquals(calculate_work_hours_in_month(year=2017, month=2, workweek_starts=5, workweek_ends=2), 20 * 8)
