#-*- coding:utf-8 -*-
import unittest
from django.test.client import Client

from tag_app.views import tag_autocomplete, combine_tags
from tagging.models import Tag
from tribes.models import Tribe, TribeMember, Topic
from django.contrib.auth.models import User, AnonymousUser
from profiles.models import Affiliation, Occupation

from tribes.models import Tribe, TribeMember, Topic
from django_dms.apps.small_dms.models import Document 
from wiki.models import Article


class TagAppTestCase(unittest.TestCase):
    
    # add 5 tags, 3 tagged objects, test and/or returns the right ones
    
    def setUp(self):
        self.sean = User.objects.create_user(u'Sean', '', '123')
        self.anonuser = AnonymousUser()
        
        self.tribe1 = Tribe(name =u'Biblnet', slug=u'biblnet', 
            creator = self.sean, description=u'Everybodys favorite tribe',
            private = False )
        self.tribe1.save()
        
        
        
        self.tribe2 = Tribe(name =u'My Group', slug=u'mygroup', 
            creator = self.sean, description=u'slaskedong',
            private = False )            
        self.tribe2.save()

        self.tribe3 = Tribe(name =u'deleted', slug=u'deleted_biblnet', 
            creator = self.sean, description=u'Everybodys favorite tribe',
            private = False )
        self.tribe3.save()

    def tearDown(self):
        Tribe.objects.all().delete()
        User.objects.all().delete()  
        
    def test_combine_tags(self):
        pass
