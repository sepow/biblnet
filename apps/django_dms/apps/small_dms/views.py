from django_dms.views import DocumentView, DocumentAdmin
from django_dms.apps.small_dms.models import Document
from django.db import models
from django.contrib.humanize.templatetags.humanize import naturalday

class DocumentView(DocumentView):

    list_display = ['summary']
    list_thumbnail = True
    list_links = ['download']
    links = ['download']
    thumbnail = False
    queryset = Document.objects.all()
    fields = ['summary', 'date_created']
    ordering = ['title']
    url_identifier_field = 'slug'
    field_class_filters = { models.DateTimeField: lambda v: naturalday(v, 'F Y').title() }
    template = 'small_dms/dms_detail.html'
    list_template = 'small_dms/dms_list.html'

        
document_view = DocumentView(name="document_view")

class DocumentUpload(DocumentAdmin):
    document_view = document_view
    model = Document
    template = 'django_dms/admin.html'
    fields = None
    exclude = None
        
document_upload = DocumentUpload(name="document_upload")
