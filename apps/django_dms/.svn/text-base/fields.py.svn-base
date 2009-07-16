#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: Model fields for django DMS apps
    Project: django_dms
     Author: Will Hardy
       Date: November 2008
  $Revision$

"""

from django import forms
from django.db import models
from django.utils.text import capfirst
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings

from django_dms.utils import ChoicesBank
from django_dms.widgets import DocumentWidget, ManyDocumentsWidget

class DocumentField(models.ForeignKey, models.FileField):
    """ Links to a document, with all the features of a FileField().
    """
    # TODO: get rid of this field --- too hard-basket, difficult to maintain
    def __init__(self, *args, **kwargs):
        super(DocumentField, self).__init__(*args, **kwargs)

        # Some FileField functionality demands an upload_to field, 
        # but this is set on the related model, not here.
        self.upload_to = 'dummy'

    def get_internal_type(self):
        return models.ForeignKey.__name__

    def save_form_data(self, instance, data):
        " Allow a form to submit a file object, and automatically handle the ForeignKey. "
        if data and isinstance(data, UploadedFile):
            if not getattr(instance, self.name + '_id'):
                doc_instance = self.rel.to()
                doc_instance.file.save(data.name, data, save=True)
                setattr(instance, self.name, doc_instance)
            else:
                getattr(instance, self.name).file.save(data.name, data, save=True)
            
    def formfield(self, **kwargs):
        kwargs['widget'] = DocumentWidget
        return models.FileField.formfield(self, **kwargs)


class ManyDocumentsField(models.ManyToManyField):
    """ Links to a document, with all the features of a FileField().
        This is simply a prefabricated ManyToManyField.
    """
    # TODO: get rid of this field --- too hard-basket, difficult to maintain
    def __init__(self, to, *args, **kwargs):
        super(ManyDocumentsField, self).__init__(to, *args, **kwargs)
        selfchoices = ChoicesBank(to._default_manager.all())
        self.help_text = kwargs.get('help_text', "")

    def get_internal_type(self):
        return models.ManyToManyField.__name__

    def formfield(self, **kwargs):
        kwargs['widget'] = ManyDocumentsWidget
        kwargs['choices'] = self.choices
        # kwargs['coerce'] = self.to_python # I wouldn't mind having this...
        kwargs['required'] = not self.blank
        kwargs['label'] = capfirst(self.verbose_name)
        if self.has_default():
            defaults['initial'] = self.get_default()

        # No call to super(), we are taking complete control of this method
        return _FlexibleTypedChoiceField(**kwargs)

#
# FORM FIELDS
#

class _FlexibleTypedChoiceField(forms.MultipleChoiceField):
    """ Standard ChoiceFields coerce the choices value to a list,
        this can force the value of the list to be calculated too early.
        Our "Flexible" version does not coerce choices, allowing its value 
        to be determined lazily.
    """
    # TODO: remove this class if ManyDocumentsField is removed

    def _get_choices(self):
        return self._choices
    def _set_choices(self, value):
        " Set the widget's choices-variable too. "
        self._choices = self.widget.choices = value
    choices = property(_get_choices, _set_choices)


