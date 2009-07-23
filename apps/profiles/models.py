# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from tribes.models import Tribe
from datetime import datetime

from timezones.fields import TimeZoneField

class Affiliation(models.Model):
    ''' An affiliation describes a users affiliation with one of the outside 
        groups. This class is used to show an icon depending on which affil you
        belond to.
    '''

    affiliation = models.CharField(_('affiliation'), max_length=40, null=True)
    icon = models.ImageField(upload_to="images/affiliateicons")
    slug = models.SlugField(max_length=30, null=True)
    tribe = models.OneToOneField(Tribe, primary_key=True)
    
    def __unicode__(self):
        return self.affiliation

    #def get_absolute_url(self):
    #return ('profile_detail', None, {'affiliation': self.slug})

    #get_absolute_url = models.permalink(get_absolute_url)

    class Meta:
        verbose_name = _('affiliation')
        verbose_name_plural = _('affiliations')
        
class Occupation(models.Model):
    ''' An Profession describes a users profession 
        
        This class is used to show an icon depending on which profession you
        belond to.
    '''

    occupation = models.CharField(_('occupation'), max_length=40, null=True)
    icon = models.ImageField(upload_to="images/professionicons")
    slug = models.SlugField(max_length=30, null=True)
    
    def __unicode__(self):
        return self.occupation


    class Meta:
        verbose_name = _('occupation')
        verbose_name_plural = _('occupations')
        
class Profile(models.Model):
    
    user = models.ForeignKey(User, unique=True, verbose_name=_('user'))
    name = models.CharField(_('name'), max_length=60, null=True)
    nickname = models.CharField(_('nickname'), max_length=60, blank=True, null=True)
    about = models.TextField(_('about'), null=True, blank=True)
    address = models.TextField(_('address'), max_length=600, null=True, blank=True)
    phone_number = models.CharField(_('phone number'), max_length=12, null=True, blank=True)
    affiliation = models.ForeignKey(Affiliation, verbose_name=_('affiliation'), null=True, blank=True)
    occupation = models.ForeignKey(Occupation, verbose_name=_('occupation'), null=True, blank=True)
    
    
    last_visit = models.DateTimeField(_('last visit'), default=datetime.now)
    last_visit_storage = models.DateTimeField(_('last visit (storage)'), default=datetime.now)
    
    reading_now = models.CharField(_('reading'), max_length=150, null=True, blank=True)
    listening_now = models.CharField(_('listening to'), max_length=150, null=True, blank=True)


    def __unicode__(self):
        return self.user.username
    
    def get_absolute_url(self):
        return ('profile_detail', None, {'username': self.user.username})
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

def create_profile(sender, instance=None, **kwargs):
    if instance is None:
        return
    profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User)
