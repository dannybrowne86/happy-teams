# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.contrib import admin

# Register your models here.
admin.site.register(apps.get_app_config('planning').models.values(), admin.ModelAdmin)
