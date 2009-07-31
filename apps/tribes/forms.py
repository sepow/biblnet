from django import forms
from django.utils.translation import ugettext_lazy as _
from sepow.widgets import AutoCompleteTagInput
from tribes.models import Tribe, Topic
from tagging.forms import TagField

class TribeForm(forms.ModelForm):
    tags = TagField(widget=AutoCompleteTagInput(cls=Tribe), required=False)
    slug = forms.SlugField(max_length=20,
        help_text = _("A short version of the name consisting only of letters (a-z), numbers, underscores and hyphens."),
        error_message = _("This value must contain only letters, numbers, underscores and hyphens."))
            
    def clean_slug(self):
        reserved_slugs = ["your_tribes"]
        if self.cleaned_data["slug"] in reserved_slugs:
            raise forms.ValidationError(_("The slug you've chosen is reserved for internal use."))
        if Tribe.objects.filter(slug__iexact=self.cleaned_data["slug"]).count() > 0:
            raise forms.ValidationError(_("A tribe already exists with that slug."))
        return self.cleaned_data["slug"].lower()
    
    def clean_name(self):
        if Tribe.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            raise forms.ValidationError(_("A tribe already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Tribe
        fields = ('name', 'slug', 'tags', 'description', 'private')


# @@@ is this the right approach, to have two forms where creation and update fields differ?

class TribeUpdateForm(forms.ModelForm):

    tags = TagField(widget=AutoCompleteTagInput(cls=Tribe), required=False)    
    def clean_name(self):
        if Tribe.objects.filter(name__iexact=self.cleaned_data["name"]).count() > 0:
            if self.cleaned_data["name"] == self.instance.name:
                pass # same instance
            else:
                raise forms.ValidationError(_("A tribe already exists with that name."))
        return self.cleaned_data["name"]
    
    class Meta:
        model = Tribe
        fields = ('name', 'description', 'tags', 'private')


class TopicForm(forms.ModelForm):
    tags = TagField(widget=AutoCompleteTagInput(cls=Topic), required=False)
    class Meta:
        model = Topic
        fields = ('title', 'body', 'tags')
from tribes.models import TribeMember, Tribe
from django.contrib.auth.models import User

class RemoveMemberForm(forms.Form):
    
    def __init__(self, tribe, user, *args, **kwargs):
        super(RemoveMemberForm, self).__init__(*args, **kwargs)
        self.tribe = tribe
        self.user = user

class AddMemberForm(forms.Form):

    user = forms.CharField(label=_(u"User"))

    def __init__(self, tribe, *args, **kwargs):
        super(AddMemberForm, self).__init__(*args, **kwargs)
        self.tribe = tribe

    def clean_user(self):
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['user'])
        except User.DoesNotExist:
            raise forms.ValidationError(_("There is no user with this username."))

        if TribeMember.objects.filter(tribe=self.tribe, user=user).count() > 0:
            raise forms.ValidationError(_("User is already a member of this tribe."))
        return self.cleaned_data['user']
  
    # @@@ we don't need to pass in project any more as we have self.project
    def save(self):
        username = self.cleaned_data["user"]
        new_member = User.objects.get(username__iexact=username)
        tribe_member = TribeMember(tribe=self.tribe, user=new_member)
        tribe_member.save()
        '''
        if notification:
            notification.send(project.member_users.all(), "projects_new_member", {"new_member": new_member, "project": project})
            notification.send([new_member], "projects_added_as_member", {"adder": user, "project": project})
        user.message_set.create(message="added %s to project" % new_member)
        '''
