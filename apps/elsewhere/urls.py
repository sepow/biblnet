import settings
import os

from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('elsewhere.views',
    (r'^$', 'example'),
)
