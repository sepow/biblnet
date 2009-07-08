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
from django_dms.apps.large_dms.models import Document, DocumentInteraction, Tag

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_id', 'author', 'uploaded_by', 'file_mimetype', 'file_extension', 'date_created', 'tags')

class DocumentInteractionAdmin(admin.ModelAdmin):
    list_display = ('document', 'mode', 'user', 'session_key', 'timestamp')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentInteraction, DocumentInteractionAdmin)
admin.site.register(Tag, TagAdmin)
