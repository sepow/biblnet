from django import forms
from django.utils.translation import ugettext_lazy as _
from django_dms.apps.small_dms.models import Document
from tagging.forms import TagField
from sepow.widgets import AutoCompleteTagInput

class UploadForm(forms.ModelForm):
    tags = TagField(widget=AutoCompleteTagInput(cls=Document), required=False) 
    class Meta:
        model = Document
        fields = ('file', 'title', 'slug', 'summary', 'tags', 'grade',)
