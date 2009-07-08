#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: Basic admin for and out-of-the-box DMS
    Project: django_dms
     Author: Will Hardy
       Date: November 2008
  $Revision$
"""

from django.contrib import admin
from django_dms.basicdocuments.models import BasicDocument

class BasicDocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'title', 'author', 'file_mimetype', 'uploaded_by', 'date_added', 'date_created')

admin.site.register(BasicDocument, BasicDocumentAdmin)
