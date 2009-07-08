#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: 
    Project: 
     Author: Will Hardy
       Date:  2008
      Usage: 
  $Revision: 24 $

Description: 

"""

from django.conf.urls.defaults import *
from django_dms.apps.small_dms.views import document_view, document_upload

urlpatterns = patterns('',
    url(r'^upload/',  include(document_upload.urls), name="document_upload" ),
    url(r'^',  include(document_view.urls), name="document_view" ),
)
