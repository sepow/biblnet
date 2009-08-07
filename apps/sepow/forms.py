# -*- coding: utf-8 -*-
import re

from django import forms
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.encoding import smart_unicode
from django.utils.hashcompat import sha_constructor
from misc.utils import get_send_mail
send_mail = get_send_mail()

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from emailconfirmation.models import EmailAddress
from account.models import Account

from timezones.forms import TimeZoneField

from account.models import PasswordReset
from captcha.fields import CaptchaField
from profiles.models import Affiliation, Occupation, Profile
from tribes.models import TribeMember, Tribe
from datetime import datetime
#alnum_re = re.compile(r'^\w+$')

alnum_re = re.compile(r'^[\wæøå]+$', re.U)

class BiblnetSignupForm(forms.Form):
    captcha = CaptchaField()
    username = forms.CharField(label=_(u"Username"), max_length=30, widget=forms.TextInput())
    name = forms.CharField(label=_(u"Full name"), max_length=50, widget=forms.TextInput())
    email = forms.EmailField(label=_(u"Email"), required=True, widget=forms.TextInput())
    password1 = forms.CharField(label=_(u"Password"), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_(u"Password (again)"), widget=forms.PasswordInput(render_value=False))
    affiliation = forms.ModelChoiceField(queryset=Affiliation.objects.filter(tribe__private__exact=False), empty_label=_("(Pick your affiliation)")) #TODO clean
    occupation = forms.ModelChoiceField(queryset=Occupation.objects.all(), empty_label=_("(Pick your occupation)")) 
    confirmation_key = forms.CharField(max_length=40, required=False, widget=forms.HiddenInput())
    
    accept_terms = forms.BooleanField(required=True) 

    def clean_username(self):
        if not alnum_re.search(self.cleaned_data["username"]):
            raise forms.ValidationError(_("Usernames can only contain letters, numbers and underscores."))
        try:
            user = User.objects.get(username__iexact=self.cleaned_data["username"])
        except User.DoesNotExist:
            return self.cleaned_data["username"]
        raise forms.ValidationError(_("This username is already taken. Please choose another."))

    def clean(self):
        if "password1" in self.cleaned_data and "password2" in self.cleaned_data:
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                raise forms.ValidationError(_("You must type the same password each time."))
        return self.cleaned_data

    def save(self):
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        name = self.cleaned_data["name"]
        affiliation = self.cleaned_data["affiliation"]
        occupation = self.cleaned_data["occupation"]
        password = self.cleaned_data["password1"]
        
        if self.cleaned_data["confirmation_key"]:
            from friends.models import JoinInvitation # @@@ temporary fix for issue 93
            try:
                join_invitation = JoinInvitation.objects.get(confirmation_key = self.cleaned_data["confirmation_key"])
                confirmed = True
            except JoinInvitation.DoesNotExist:
                confirmed = False
        else:
            confirmed = False

        # @@@ clean up some of the repetition below -- DRY!

        if confirmed:
            if email == join_invitation.contact.email:
                new_user = User.objects.create_user(username, email, password)
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                new_user.message_set.create(message=ugettext(u"Your email address has already been verified"))
                # already verified so can just create
                EmailAddress(user=new_user, email=email, verified=True, primary=True).save()
            else:
                new_user = User.objects.create_user(username, "", password)
                join_invitation.accept(new_user) # should go before creation of EmailAddress below
                if email:
                    new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
                    EmailAddress.objects.add_email(new_user, email)
            return username, password # required for authenticate()
        else:

            new_user = User.objects.create_user(username, "", password)
            # def populate_profile: 
            new_profile = new_user.get_profile()
            new_profile.affiliation = affiliation
            new_profile.occupation = occupation
            new_profile.name = name
            new_profile.save()
            # Tribemember
            tmember = TribeMember(tribe=new_profile.affiliation.tribe, user=new_user)
            tmember.save()           
            # Global tribe
            try: 
                global_tribe = Tribe.objects.get(slug = u'global')
                tmember = TribeMember(tribe=global_tribe, user=new_user)
                tmember.save()
            except:
                pass
                
            if email:
                new_user.message_set.create(message=ugettext(u"Confirmation email sent to %(email)s") % {'email': email})
                EmailAddress.objects.add_email(new_user, email)
            
            return username, password # required for authenticate()
            
            
class BiblnetLoginForm(forms.Form):

    username = forms.CharField(label=_("Username"), max_length=30, widget=forms.TextInput())
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(render_value=False))
    remember = forms.BooleanField(label=_("Remember Me"), help_text=_("If checked you will stay logged in for 3 weeks"), required=False)

    user = None

    def clean(self):
        if self._errors:
            return
        user = authenticate(username=self.cleaned_data["username"], password=self.cleaned_data["password"])
        if user:
            if user.is_active:
                self.user = user
            else:
                raise forms.ValidationError(_("This account is currently inactive."))
        else:
            raise forms.ValidationError(_("The username and/or password you specified are not correct."))
        return self.cleaned_data

    def login(self, request):
        if self.is_valid():
            login(request, self.user)
            request.user.message_set.create(message=ugettext(u"Successfully logged in as %(username)s.") % {'username': self.user.username})
            if self.cleaned_data['remember']:
                request.session.set_expiry(60 * 60 * 24 * 7 * 3)
            else:
                request.session.set_expiry(0)
            
            profile = self.user.get_profile()
            profile.last_visit = profile.last_visit_storage
            
            profile.last_visit_storage = datetime.now()
            profile.save()  
            ## now use last_visit
            

            return True
        return False
