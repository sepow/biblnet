#-*- coding:utf-8 -*-
from datetime import datetime


from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from sepow.html import sanitize_html
from tagging.fields import TagField
from photos.models import Pool

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

from wiki.views import get_articles_for_object

class Tribe(models.Model):
    """
    a tribe is a group of users with a common interest
    """
    
    
    name = models.CharField(_('name'), max_length=80, unique=True)
    slug = models.SlugField(_('slug'), max_length=80, unique=True)
    creator = models.ForeignKey(User, related_name="created_groups", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    description = models.TextField(_('description'))
    deleted = models.BooleanField(_('deleted'), default=False)

    tags = TagField()
   
    
    
    photos = generic.GenericRelation(Pool)
    
    # Lidt privatliv.. 
        
    private = models.BooleanField(_('private'), default=False)
    member_users = models.ManyToManyField(User, through="TribeMember", verbose_name=_('members'))
    
    # @@@ this might be better as a filter provided by wikiapp
    def wiki_articles(self):
        return get_articles_for_object(self)

    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return ("tribe_detail", [self.slug])

    class Meta:
        ordering = ('name',)
    get_absolute_url = models.permalink(get_absolute_url)
    
class TribeMember(models.Model):
    tribe = models.ForeignKey(Tribe, related_name="members", verbose_name=_('tribe'))
    user = models.ForeignKey(User, related_name="tribes", verbose_name=_('user'))
    date_joined = models.DateTimeField(_('date_joined'), default=datetime.now)
    
    moderator = models.BooleanField(_('moderator'), default=False)
    
    last_visit = models.DateTimeField(_('last visit'), default=datetime.now)
    
    def __unicode__(self):
        return u"%s - %s" % (self.tribe, self.user)

    class Meta:
        unique_together = (("tribe", "user"),) 
        
from threadedcomments.models import ThreadedComment
class Topic(models.Model):
    """
    a discussion topic for the tribe.
    """
    
    tribe = models.ForeignKey(Tribe, related_name="topics", verbose_name=_('tribe'))
    
    title = models.CharField(_('title'), max_length=50)
    creator = models.ForeignKey(User, related_name="created_topics", verbose_name=_('creator'))
    created = models.DateTimeField(_('created'), default=datetime.now)
    modified = models.DateTimeField(_('modified'), default=datetime.now) # topic modified when commented on
    editet = models.DateTimeField(_('editet'), default=datetime.now) # topic editet
    body = models.TextField(_('body'))
    views = models.IntegerField(_("views"), default=0)
    sticky = models.BooleanField(_("sticky?"), blank=True, default=False) # skupper tråden op øverst i forumet. 
    closed = models.BooleanField(_("closed?"), blank=True, default=False) # ikke muligt at skrive indlæg til denne post

    tags = TagField()
    
    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ("tribe_topic", [self.pk])
    get_absolute_url = models.permalink(get_absolute_url)
    
    class Meta:
        ordering = ('-sticky', '-modified')



def new_comment(sender, instance, **kwargs):
    if isinstance(instance.content_object, Topic):       
        topic = instance.content_object
        topic.modified = datetime.now()
        topic.save()
        if notification:
            notification.send([topic.creator], "tribes_topic_response", {"user": instance.user, "topic": topic})
models.signals.post_save.connect(new_comment, sender=ThreadedComment)
