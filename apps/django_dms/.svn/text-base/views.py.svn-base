#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: 
    Project: 
     Author: Will Hardy
       Date:  2008
      Usage: 
  $Revision$

Description: 

       TODO: AddDocument and EditDocument views, like django admin, but with a slightly different workflow:
                1. File is uploaded, emailed or somehow sent to server
                2. Form is prepared with metadata, slugs etc populated
                3. User edits and saves form

"""
import os
import threading
from django import forms
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template import loader
from django.db import models
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url, include
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db.models.fields import FieldDoesNotExist
from django.utils.encoding import force_unicode

from django_dms.signals import document_interaction
from django_dms.models import DocumentStaging

# Check if thumbnails are supported
try:
    import sorl.thumbnail as SORL_THUMBNAIL
except ImportError:
    SORL_THUMBNAIL = None

# Store requested passwords to allow a batch of documents to be downloaded without prompt
# TODO: Should this timeout, to avoid problems with public computers?
SESSION_VAR_EMAIL_ADDRESS = 'django_dms_email_address'

class DocumentResponse(HttpResponse):
    def __init__(self, document):
        super(DocumentResponse, self).__init__(content=document.file, mimetype=document.file_mimetype or 'text/plain')
        self['Content-Disposition'] = 'attachment; filename=%s' % document.friendly_filename

class DocumentViewResponse(HttpResponse):
    """ If we can show a thumbnail (eg the first page of a PDF), do that, otherwise download the document in-browser. """
    def __init__(self, document):
        super(DocumentViewResponse, self).__init__(content=document.file, mimetype=document.file_mimetype or 'text/plain')

def email_document(document, to, template='django_dms/email.txt', subject=''):
    """ Email the given document to the given email address.
    """
    # Start a new thread to email the document
    # This avoids a frozen screen while the email is being sent (particularly if the document is big).
    t = threading.Thread(target=_email_document, args=[document, to, template, subject])
    t.setDaemon(True)
    t.start()

def _email_document(document, to, template='django_dms/email.txt', subject=''):
    """ Helper function to email document in another thread.
    """ 
    # TODO: A really cool system would delay sending the email for 10 seconds or so, 
    # to allow the user to quickly undo :-) This could probably also be done client-side (ie JS)
    # Create the message
    message = EmailMessage(to=to, subject=subject)
    message.to = to
    message.subject = subject
    message.body = render_to_string(template, {'document': document})
    message.attach(document.friendly_filename, document.file.read(), document.file_mimetype)

    # Send the message
    message.send()

class Item(object):
    pass

class EmailForm(forms.Form):
    email = forms.EmailField()

class DocumentView(object):
    queryset = None
    url_identifier_field = 'uuid' # Please use something sane like slug or friendly_id, not uuid!

    # List view customisation
    list_template = 'django_dms/list.html'
    list_thumbnail = True
    list_display = ['summary']
    list_links = ['preview', 'view', 'download', 'email']
    list_per_page = 10
    ordering = None
    search_fields = None # TODO

    # Detail view customisation
    template = 'django_dms/detail.html'
    fields = None # [] is no fields, None is all fields
    exclude = []  # [] is no fields
    field_class_filters = { models.DateTimeField: lambda v: naturalday(v, 'd F Y').title() }
    field_filters = {}
    thumbnail = True
    links = ['preview', 'view', 'download', 'email']

    def __init__(self, name=None):
        self.name = name

    def get_urls(self):
        """ Get the list of url patterns for this view. """
        return patterns('',
            url(r'^$',                      self.list, name="%s_document_list" % self.name),
            url(r'^([^\/]+)/download/$',  self.download, name="%s_document_download" % self.name),
            url(r'^([^\/]+)/send/$',      self.send, name="%s_document_send" % self.name),
            url(r'^([^\/]+)/send/ajax/$', self.send_ajax, name="%s_document_send_ajax" % self.name),
            url(r'^([^\/]+)/detail/$',    self.detail, name="%s_document_detail" % self.name),
            url(r'^([^\/]+)/view/$',      self.view, name="%s_document_view" % self.name),
            )
    urls = property(get_urls)

    #########
    # VIEWS #
    #########

    def list(self, request):
        page_number = request.GET.get('page', 1)

        queryset = self._get_prepared_queryset()

        pages = Paginator(queryset, self.list_per_page)
        page = pages.page(page_number)
        object_list = [ self._get_list_item(i) for i in page.object_list ]
        context = { 'request': request, 'object_list': object_list,
                    'list_display': dict([(a, True) for a in self.list_display]),
                    'list_thumbnail': SORL_THUMBNAIL and self.list_thumbnail,
                    'list_links': dict([(a, True) for a in self.list_links]),
                    'page': page,
                    'dms_site': self,
                    }

        return render_to_response(self.list_template, context)

    def get_document(self, id):
        queryset = self._get_prepared_queryset()
        kwargs = {self.url_identifier_field: id}
        return get_object_or_404(queryset, **kwargs)

    def send(self, request, id):
        """ Send the specified document to the user's email address (HTML version). """
        document = self.get_document(id)

        form     = self._set_user_email_address(request)
        email    = self._get_user_email_address(request)
        if form or not email:
            return render_to_response('django_dms/send.html', locals())
    
        # NB: Temporarily disabling actual email sending for development
        #email_document(document, to=[email], subject='Document: %s' % document.title)
        print "Sending email to %s" % email 
    
        # Send a signal to let everyone know about this document interaction
        document_interaction.send(sender=self, document=document, mode="sent", request=request, recipient=email)
    
        return HttpResponseRedirect(reverse('%s_document_list' % self.name))
    
    def send_ajax(self, request, id):
        """ Send the specified document to the user's email address (AJAX version). """

        document = self.get_document(id)

        form     = self._set_user_email_address(request)
        email    = self._get_user_email_address(request)
        if not email and not form:
            form = EmailForm()
    
        if form:
            content = '<form class="ajax_update_email" action="%s" method="post">' % reverse('%s_document_send' % self.name, args=[getattr(document, self.url_identifier_field)])
            content += '%s<input type="submit" value="Send"/></form>' % form['email']
            return HttpResponse(content)
    
        print "Sending email to %s" % email
        #email_document(document, to=[email], subject='Document: %s' % document.title)

        # Send a signal to let everyone know about this document interaction
        document_interaction.send(sender=self, document=document, mode="sent", request=request, recipient=email)
    
        return HttpResponse('Email sent to %s' % email)
    
    def download(self, request, id):

        document = self.get_document(id)

        # Send a signal to let everyone know about this document interaction
        document_interaction.send(sender=self, document=document, mode="downloaded", request=request)

        return DocumentResponse(document)
    
    def detail(self, request, id):

        document = self.get_document(id)

        dms_site = self
        thumbnail = SORL_THUMBNAIL and self.thumbnail
        list_links = dict([(a, True) for a in self.links])

        # Get the list of fields to include (default to all fields)
        fields   = self.fields or [ f.name for f in document._meta.fields ]
        # Remove excluded fields
        fields   = [ f for f in fields if f not in self.exclude ]
        # prepare the fields for the template
        fields   = [self._prepare_field(document, field) for field in fields ]

        return render_to_response(self.template, locals())
    
    def view(self, request, id):

        document = self.get_document(id)

        # Send a signal to let everyone know about this document interaction
        document_interaction.send(sender=self, document=document, mode="viewed", request=request)

        return DocumentViewResponse(document)
    
    
    ####################
    # INTERNAL METHODS #
    ####################
    def _get_prepared_queryset(self):
        queryset = self.queryset._clone()
        if self.ordering:
            queryset = queryset.order_by(*self.ordering)
        return queryset


    def _prepare_field(self, document, field):
        " Prepare the field for the template, much like a template filter would. "

        try:
            field_class = document._meta.get_field(field)
            verbose_name = field_class.verbose_name
        except FieldDoesNotExist:
            field_class = None
            verbose_name = ' '.join(field.split('_'))

        value = force_unicode(getattr(document, field))

        # Run standard class filters (eg DateTimeField)
        if field_class and value is not None and field_class.__class__ in self.field_class_filters:
            value = self.field_class_filters[field_class.__class__](value)

        # Run specific field filters
        if value is not None and field in self.field_filters:
            value = self.field_filters[field](value)

        return (verbose_name, value)

    def _get_user_email_address(self, request):
        """ Gets a custom defined or default email address for the current user. """
        return request.session.get(SESSION_VAR_EMAIL_ADDRESS, not request.user.is_anonymous() and request.user.email)
    
    def _set_user_email_address(self, request):
        """ If a new email address is posted, remember it.
        """
        if request.method == 'POST':
            form = EmailForm(request.POST)
            if form.is_valid():
                request.session[SESSION_VAR_EMAIL_ADDRESS] = form.cleaned_data['email']
            else:
                return form

    def _get_list_item(self, document):
        """ Get an item for the template, containing the document. """
        list_item = Item()
        list_item.document = document
        # TODO: call callables?
        list_item.display_fields = [self._prepare_field(document, field) for field in self.list_display]
        return list_item

    # Process documents before use
    def _set_documents(self, documents):
        # Add annotations
        self._documents = documents.annotate(already_sent=models.Count('interactions'))
    documents = property(lambda s:s._documents, _set_documents)


class DocumentAdmin(object):
    model = None
    form = None # Use ModelForm
    template = 'django_dms/admin.html'
    fields = None
    exclude = None
    # Keys can be: email_subject, email_content, email_sender, email_date, email_received_date, 
    #              file_mimetype, file_original_name, file_original_name_stem, file_original_name_extension, file
    email_populate = {}
    document_view = None

    def __init__(self, name=None):
        self.name = name

    def get_urls(self):
        """ Get the list of url patterns for this view. """
        return patterns('',
            #url(r'^$',                      self.list, name="%s_document_list" % self.name),
            #url(r'^(.+)/edit/$',  self.edit, name="%s_document_edit" % self.name),
            url(r'^([\w\d-]+)/confirm/$',  self.confirm, name="%s_document_confirm" % self.name)
            )
    urls = property(get_urls)

    def edit(self, request, pk):
        instance = get_object_or_404(self.model, pk=pk)
        Form = self.get_form()
        if request.method == "POST":
            form = Form(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('%s_document_detail' % data.dms_site, args=[getattr(instance, data.dms_site.url_identifier_field)]))
        else:
            form = Form(instance=instance)
        return HttpResponse(form)
        return render_to_response('django_dms/edit.html')

    def get_form(self):
        # 2. Create form
        if self.form:
            Form = self.form
        else:
            class Form(forms.ModelForm):
                class Meta:
                    model = self.model
                    fields = self.fields or None
                    exclude = (self.exclude or []) + ['file']
        return Form

    def confirm(self, request, uuid):
        # 1. Find data or 404
        data = get_object_or_404(DocumentStaging, uuid=uuid)

        Form = self.get_form()

        # 3. Handle POSTed form
        if request.method == "POST":
            form = Form(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                #instance.file.save(data.file_original_name, data.file, save=False)
                setattr(instance, self.email_populate.get('file', 'file'), data.file)
                instance.save()

                return HttpResponseRedirect(reverse('%s_document_detail' % data.dms_site, args=[getattr(instance, data.dms_site.url_identifier_field)]))

        # 4. Handle new form
        else:

            # 4a. Populate visible form
            # TODO: Allow custom population? (The only fields available are filename, subject, email body etc)
            instance = self.model()
            filename_stem, filename_extension = os.path.splitext(data.file_original_name)
    
            # Keys can be email_subject, email_content, email_author, email_date, email_received_date, 
            #             file_mimetype, file_original_name, file_original_name_stem, file_original_name_extension, file
            email_populate = self.email_populate.copy()
    
            # Process virtual fields: file_original_name_stem, file_original_name_extension
            if 'file_original_name_stem' in email_populate:
                setattr(instance, email_populate.pop('file_original_name_stem'), filename_stem)
            if 'file_original_name_extension' in email_populate:
                setattr(instance, email_populate.pop('file_original_name_extension'), filename_extension)
            else:
                instance.file_extension = filename_extension

            # Process certain fields by default
            setattr(instance, email_populate.pop('file_mimetype', 'file_mimetype'), data.file_mimetype)
            # The file field is processed at the end, when we have the data.
            email_populate.pop('file', None)
    
            # Process all other fields explicitly
            for key, value in email_populate.items():
                setattr(instance, value, getattr(data, key))

            form = Form(instance=instance)

        context = {}
        context['form'] = form
        context['request'] = request

        return render_to_response(self.template, context)
