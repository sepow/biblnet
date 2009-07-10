from django import forms
from profiles.models import Profile
from profiles.models import Affiliation, Occupation
from django.utils.translation import ugettext_lazy as _, ugettext
class ProfileForm(forms.ModelForm):
    affiliation = forms.ModelChoiceField(queryset=Affiliation.objects.filter(tribe__private__exact=False), empty_label=_("(Pick your affiliation)"))
    occupation = forms.ModelChoiceField(queryset=Occupation.objects.all(), empty_label=_("(Pick your occupation)"))
    class Meta:
        model = Profile
        exclude = ('user', 'blogrss', 'timezone',
            'twitter_user', 'twitter_password')
