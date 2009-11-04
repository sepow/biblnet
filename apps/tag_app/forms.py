from django import forms
from django.utils.translation import ugettext_lazy as _
from tagging.utils import parse_tag_input


class CombineTagsForm(forms.Form):
    
    CHOICES = (("AND", "AND"),("OR", "OR"))
    
    tags = forms.CharField(label=_("Tags"))
    bool = forms.ChoiceField(choices=CHOICES, initial="AND", help_text="Insert your shit here")
    
    def clean_tags(self):
        return parse_tag_input(self.cleaned_data["tags"])