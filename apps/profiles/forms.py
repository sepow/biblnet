from django import forms
from profiles.models import Profile
from profiles.models import Affiliation
from django.utils.translation import ugettext_lazy as _, ugettext
class ProfileForm(forms.ModelForm):
    affiliation = forms.ModelChoiceField(queryset=Affiliation.objects.filter(tribe__private__exact=False), empty_label=_("(Pick your affiliation)"))
    class Meta:
        model = Profile
        exclude = ('user', 'blogrss', 'timezone', 'language',
            'twitter_user', 'twitter_password')
