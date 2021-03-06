#-*- coding:utf-8 -*-
from haystack.sites import site
from haystack import indexes
from tribes.models import Topic, Tribe
from profiles.models import Profile

from django_dms.apps.small_dms.models import Document
from wiki.models import Article
from threadedcomments.models import ThreadedComment

import datetime


class TopicIndex(indexes.SearchIndex):
    
    text = indexes.CharField(document=True, use_template=True, model_attr='body')
    author = indexes.CharField(model_attr='creator')
    # crasher reindex..    created = indexes.DateTimeField()
    title = indexes.CharField(model_attr='title', indexed=True)

    def get_query_set(self):
        "Used when the entire index for model is updated."
        return Topic.objects.filter(tribe__private=False)

    def should_update(self):
        # opdater if editet er blvet changed indenfor 5 secs. 
        return True
        
#site.register(Topic)
#site.register(Tribe)
site.register(Document)
site.register(Article)
site.register(Profile)
site.register(ThreadedComment)

