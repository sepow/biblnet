"""
Based on http://www.djangosnippets.org/snippets/595/
by sopelkin
"""

from django import forms
from django.forms import widgets
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class CommaSeparatedUserInput(widgets.Input):
    input_type = 'text'
    
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif isinstance(value, (list, tuple)):
            value = (', '.join([user.username for user in value]))
        return super(CommaSeparatedUserInput, self).render(name, value, attrs)
        


class CommaSeparatedUserField(forms.Field):
    widget = CommaSeparatedUserInput
    
    def clean(self, value):
        super(CommaSeparatedUserField, self).clean(value)
        if not value:
            return ''
        if isinstance(value, (list, tuple)):
            return value
        
        names = set(value.split(','))
        names_set = set([name.strip().lower() for name in names if name.strip()])

        if len(names_set) >= 30:
            raise forms.ValidationError(_(u"You can't message this many people at once."))
        
        users = []
        for u in names_set:
                users += User.objects.filter(username__iexact=u)

        unknown_names = names_set ^ set([user.username.lower() for user in users])
        if unknown_names:
            raise forms.ValidationError(_(u"The following user(s) do not exist: %(users)s") % {'users': ', '.join(unknown_names)})
        
        return users
