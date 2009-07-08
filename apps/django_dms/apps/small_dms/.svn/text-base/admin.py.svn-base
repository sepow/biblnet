#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: 
    Project: 
     Author: Will Hardy
       Date: January 2009
      Usage: 
  $Revision$

Description: 

"""
from django.contrib import admin
from django_dms.apps.small_dms.models import Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'file_mimetype', 'file_extension', 'date_created')
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Document, DocumentAdmin)
