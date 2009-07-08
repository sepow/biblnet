#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: DMS framework widgets
    Project: django_dms
     Author: Will Hardy
       Date: November 2008
  $Revision$

"""

from django.db.models import get_model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django import forms

from django.forms.util import flatatt
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode, smart_unicode


class DocumentWidget(forms.FileInput):
    """
    Like a FileField Widget, but for DocumentFields, which have an intermediate model.
    """
    #def __init__(self, attrs={}):
        #super(DocumentWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        document = None
        document_file = None

        # Sadly, a database query may be necessary
        # TODO: Is there any way to put this in the Field?
        if value and isinstance(value, basestring):
            # TODO: Use choices to find document?, not BasicDocument
            document = get_model('basicdocuments', 'BasicDocument').objects.get(pk=value)
            document_file = document.file

        if value and hasattr(document_file, "url"):
            # TODO: Remove hardcoded URL somehow
            # TODO: Make this more usable!
            output.append('%s <a target="_blank" href="../../../documents/basicdocument/%s/">%s</a> &nbsp;&nbsp;(<a href="../../../documents/basicdocument/%s/delete/">remove</a>)<br />%s ' % \
                (_('Currently:'), document.pk, document.pk, document.title or document.uuid, _('Change:')))
        output.append(super(DocumentWidget, self).render(name, document_file, attrs))
        return mark_safe(u''.join(output))


class ManyDocumentsWidget(forms.SelectMultiple):

    def __init__(self, attrs=None, choices=()):
        # forms.Widget.__init__(self, attrs)
        self.attrs = attrs and attrs.copy or {}
        self.choices = choices

    def render_options(self, choices, selected_choices):
        # Limit the choices to the selected values
        if hasattr(self.choices, 'queryset'):
            choices = self.choices.only(selected_choices)

        # Normalize to strings.
        selected_choices = set([force_unicode(v) for v in selected_choices])
        output = []
        for option_value, option_label in choices:
            if isinstance(option_label, (list, tuple)):
                for val, lab in option_label:
                    output.append(u'<li><a href="%s">%s</a>' % ( escape(force_unicode(val)), conditional_escape(force_unicode(lab))))
            else:
                output.append(u'<li><a href="%s">%s</a>' % ( escape(force_unicode(option_value)), conditional_escape(force_unicode(option_label))))
        # TODO: Append new document field, there is currently no way to add new documents!

        return u'\n'.join(output)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</ul>')
        return mark_safe(u'\n'.join(output))

