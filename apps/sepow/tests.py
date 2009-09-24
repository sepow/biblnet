#-*- coding:utf-8 -*-
import unittest
from django.test.client import Client

from sepow.templatetags.biblnet_tags import *
from sepow.templatetags.security_tag import *
from tribes.models import Tribe, TribeMember
from django.contrib.auth.models import User, AnonymousUser
from profiles.models import Affiliation, Occupation
'''
Tests:

biblnet_tags:
    has_member
security_tags:
    
'''
class BiblnetTestCase(unittest.TestCase):
    
    
    def setUp(self):
        self.sean = User.objects.create_user(u'Sean', '', '123')
        self.normaluser = User.objects.create_user(u'Normaluser', '', '123')
        self.anonuser = AnonymousUser()
        
        self.tribe1 = Tribe(name =u'Biblnet', slug=u'biblnet', 
            creator = self.sean, description=u'Everybodys favorite tribe',
            private = False )
        self.tribe1.save()
        
        self.tribe2 = Tribe(name =u'My Group', slug=u'mygroup', 
            creator = self.normaluser, description=u'slaske',
            private = False )            
        self.tribe2.save()
        
        tm = TribeMember.objects.create(tribe=self.tribe1, user=self.sean, moderator=True)
        tm.save()

        tm = TribeMember.objects.create(tribe=self.tribe2, user=self.normaluser, moderator=True)
        tm.save()
            
    def test_has_member(self):
        
        # ----- has_member ----- # 
        
        # Sean is a member of tribe1, so it should return true
        self.assertEquals(has_member(self.tribe1, self.sean), True)
        # Sean isn't a member of this tribe, so it should return false
        self.assertEquals(has_member(self.tribe2, self.sean), False)
        # Anonymous users should get False
        self.assertEquals(has_member(self.tribe2, self.anonuser), False)
        self.assertEquals(has_member(self.tribe1, self.anonuser), False)
    
    def test_nr2(self):
        pass
