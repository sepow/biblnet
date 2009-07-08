from django import forms
from django.utils.translation import ugettext_lazy as _
from django_dms.apps.small_dms.models import Document

class UploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('file', 'title', 'slug', 'summary', 'tags',)
