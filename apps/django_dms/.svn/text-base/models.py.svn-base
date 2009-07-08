#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: DMS framework models
    Project: django_dms
     Author: Will Hardy
       Date: November 2008
  $Revision$
"""

import os
import uuid
from datetime import datetime

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.encoding import force_unicode, smart_unicode

from django_dms.utils import ChoicesBank, Choices, UUIDField, HashField, get_hash
from mimetypes import guess_type

try:
    from sorl.thumbnail.main import DjangoThumbnail
except ImportError:
    DjangoThumbnail = None

def get_filename_from_uuid(instance, filename, directory='documents'):
    populate_file_extension_and_mimetype(instance, filename)
    stem, extension = os.path.splitext(filename)
    return '%s/%s%s' % (directory, instance.uuid, extension)

def populate_file_extension_and_mimetype(instance, filename):
    # First populate the file extension and mimetype
    instance.file_mimetype, encoding = guess_type(filename) or ""
    slug, instance.file_extension = os.path.splitext(filename)
    #instance.slug, instance.extension = os.path.splitext(filename)

class DocumentBase(models.Model):
    """ Minimum fields for a document entry.
        Inherit this model to customise document metadata, see BasicDocument for an example.
    """
    uuid           = models.CharField(max_length=36, default=lambda:unicode(uuid.uuid4()), blank=True, editable=False)#, primary_key=True)
    # TODO: The django admin uses the file extension to determine the filetype for the preview
    # A new widget will have to be created, in a similar fashion to the automatic one
    file           = models.FileField(upload_to=get_filename_from_uuid)#lambda i,f: 'documents/%s' % i.uuid)
    file_mimetype  = models.CharField(max_length=50, default="", editable=False)
    file_extension = models.CharField(max_length=10, default="", editable=False)

    date_added   = models.DateTimeField("added", auto_now_add=True)
    date_updated = models.DateTimeField("updated", auto_now=True) # TODO: Only change this if the file field has changed

    class Meta:
        abstract = True

    def save_file(self, contents, save=False):
        " Save a file, creating a new document_version if necessary. "
        self.file.save(contents.name, contents, save=save)
        # This is now done elsewhere
        #self.file_mimetype = guess_type(contents.name) or ""
        #try:
            #self.file_extension = contents[contents.rindex(".")+1:] or ""
        #except ValueError:
            #pass
        #self.save()

    def __unicode__(self):
        return self.uuid

    @property
    def friendly_filename(self):
        """ A friendly filename (ie not the UUID) for the user to see when they download.
            Overload this with eg a slug field. 
        """
        return 'untitled.%s' % self.file_extension


    def already(self, mode, request):
        """ Tests if a user has already viewed, downloaded or sent this document. 
            Assumes this model has a log of document interactions.
        """
        mode = getattr(DocumentInteractionBase.MODES, mode.upper())

        if request.user.is_anonymous():
            return bool(self.interactions.filter(mode=mode, session_key=request.session.session_key))
        else:
            return bool(self.interactions.filter(mode=mode, user=request.user))

    @property               
    def file_thumbnail_small(self):
        # TODO: subclass DjangoThumbnail to remove UUID from URL
        if DjangoThumbnail:
            return DjangoThumbnail(self.file.name, (200,200))

    @property               
    def file_thumbnail_medium(self):
        # TODO: subclass DjangoThumbnail to remove UUID from URL
        if DjangoThumbnail:
            return DjangoThumbnail(self.file.name, (600,600))

class InteractionManager(models.Manager):
    use_for_related_fields = True
    def register(self, document, mode, request, recipient=None, **kwargs):
        attributes = { 'document': document, 'mode': getattr(self.model.MODES, mode.upper()) }
        if request.user.is_anonymous():
            attributes['session_key'] = request.session.session_key
        else:
            attributes['user'] = request.user
        return self.create(**attributes)

class DocumentInteractionBase(models.Model):
    MODES = Choices('Viewed', 'Downloaded', 'Sent')

    #document    = models.ForeignKey(Document, related_name="interactions")
    mode        = models.PositiveSmallIntegerField(choices=MODES)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    user        = models.ForeignKey(User, null=True, blank=True)
    timestamp   = models.DateTimeField(default=datetime.now)
    objects     = InteractionManager()

    def __unicode__(self):
        return u'%s %s by %s on %s' % (self.document, self.get_mode_display().lower(), 
                                        self.user or self.session_key, self.timestamp.date())

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            # Set the mode automatically, based on which class is saving this object.
            self.mode = self.__class__.MODE
        except AttributeError:
            pass
        super(DocumentInteractionBase, self).save(*args, **kwargs)


#def interaction_model_factory(document_model):
    #""" Create a class that will correctly implement document interactions. """
    ## TODO: This is not the best approach, because the class name is not explicitly determined by the user.
    ## TODO: Is there a way of using the user's chosen name for this?
    ## TODO: register this class and any subclasses?
    #class DocumentInteraction(DocumentInteractionBase):
        #document    = models.ForeignKey(document_model, related_name="interactions")
    #return DocumentInteraction

from django.core.files.base import ContentFile, File

class StagingManager(models.Manager):
    def add_staging_document(self, content, filename, content_type, email_data, dms_site):
        attributes = { 'file_original_name': filename, 
                       'file_mimetype': content_type, 'email_subject': email_data.subject, 
                       'email_content': email_data.content, 'email_sender': email_data.sender, 
                       'email_date': email_data.date, 'dms_site': dms_site.name }
        instance = self.model(**attributes)
        instance.file.save(filename, ContentFile(content), save=True)
        return instance

# Set DJANGO_DMS_STAGING to False to prevent table from being created
if getattr(settings, 'DJANGO_DMS_STAGING', True):

    staging_filename = lambda i,f: get_filename_from_uuid(i, f, directory='staging')
    class DocumentStaging(models.Model):
        """ Storage for documents between uploading and adding to the database proper.
            TODO: Another, more flexible approach would be to simply store the email headers
            and parse it when populating the instance. This means that custom population fields
            can references headers that we haven't stored here. This could be rewritten at a future date, 
            if it really is necessary.
        """

        uuid                = models.CharField(max_length=36, default=lambda:unicode(uuid.uuid4()), blank=True)
        file                = models.FileField(upload_to=staging_filename)
        file_mimetype       = models.CharField(max_length=50, default="", blank=True)
        file_original_name  = models.CharField(max_length=255, default="", blank=True)
        email_subject       = models.TextField(default="", blank=True)
        email_content       = models.TextField(default="", blank=True)
        email_sender        = models.CharField(max_length=255, default="", blank=True)
        email_date          = models.DateTimeField(default=datetime.now, null=True, blank=True)
        email_received_date = models.DateTimeField(auto_now_add=True)
        dms_site            = models.CharField(max_length=255, default="", blank=True)
        objects             = StagingManager()

        def __unicode__(self):
            return self.uuid

