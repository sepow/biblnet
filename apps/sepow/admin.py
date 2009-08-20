# -*- coding: utf-8 -*-

from django.contrib import admin
import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
REGEX = re.compile(r'^[\wæøå\-]+$', re.U)
class MyUserCreationForm(UserCreationForm):
    username = forms.RegexField(
        label='Username', 
        max_length=30, 
        regex=REGEX,
        help_text = 'Required. 30 characters or fewer. Alphanumeric characters only (letters, digits, hyphens and underscores).',
        error_message = 'This value must contain only letters, numbers, hyphens and underscores.')

class MyUserChangeForm(UserChangeForm):
    username = forms.RegexField(
        label='Username', 
        max_length=30, 
        regex=REGEX,
        help_text = 'Required. 30 characters or fewer. Alphanumeric characters only (letters, digits, hyphens and underscores).',
        error_message = 'This value must contain only letters, numbers, hyphens and underscores.')

class MyUserAdmin(UserAdmin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm

admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

