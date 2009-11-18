#-*- coding:utf-8 -*-
import unittest
from django.test.client import Client

from sepow.templatetags.biblnet_tags import *
from sepow.templatetags.security_tag import *
from tribes.models import Tribe, TribeMember
from django.contrib.auth.models import User, AnonymousUser
from profiles.models import Affiliation, Occupation
from sepow.utils import admin_group_access, check_if_is_moderator, do_403_if_not_superuser
'''
Tests:

utils:
    admin_group_access
    check_if_is_moderator
    
biblnet_tags:
    has_member
security_tags:
    
'''
class BiblnetTestCase(unittest.TestCase):
    
    
    def setUp(self):
        self.sean = User.objects.create_user(u'Sean', '', '123')
        self.normaluser = User.objects.create_user(u'Normaluser', '', '123')
        self.normaluser2 = User.objects.create_user(u'Normaluser2', '', '123')
        self.anonuser = AnonymousUser()
        self.superuser = User.objects.create_user(u'TehAdmin', '', '123')
        
        self.superuser.is_superuser = True
        
        self.tribe1 = Tribe(name =u'Biblnet', slug=u'biblnet', 
            creator = self.sean, description=u'Everybodys favorite tribe',
            private = False )
        self.tribe1.save()
        
        self.tribe2 = Tribe(name =u'My Group', slug=u'mygroup', 
            creator = self.normaluser, description=u'slaske',
            private = False )            
        self.tribe2.save()
        
        self.tribe3 = Tribe(name =u'privatetribe', slug=u'privatetribe', 
            creator = self.normaluser, description=u'slaske',
            private = True )            
        self.tribe3.save()

        self.administrators_tribe = Tribe(name =u'Administrators', slug=u'administrators', 
            creator = self.normaluser, description=u'slaske',
            private = True )            
        self.administrators_tribe.save()
        
        tm = TribeMember.objects.create(tribe=self.tribe1, user=self.sean, moderator=True)
        tm.save()

        tm = TribeMember.objects.create(tribe=self.tribe2, user=self.normaluser, moderator=True)
        tm.save()
        
        tm = TribeMember.objects.create(tribe=self.administrators_tribe, user=self.sean)
        tm.save()
        
        tm = TribeMember.objects.create(tribe=self.tribe3, user=self.normaluser)
        tm.save()
    
    def tearDown(self):
        Tribe.objects.all().delete()
        User.objects.all().delete()  
        TribeMember.objects.all().delete()
        
    def test_has_member(self):
        
        # ----- has_member ----- # 
        
        # Sean is a member of tribe1, so it should return true
        self.assertEquals(has_member(self.tribe1, self.sean), True)
        # Sean isn't a member of this tribe, so it should return false
        self.assertEquals(has_member(self.tribe2, self.sean), False)
        # Anonymous users should get False
        self.assertEquals(has_member(self.tribe2, self.anonuser), False)
        self.assertEquals(has_member(self.tribe1, self.anonuser), False)
    
    def test_admin_group_access(self):
        # sean go superuser har admin rettigheder
        # normaluser skal fejle. 
        
        # admin_group_access(user)
        self.assertEquals(admin_group_access(self.anonuser), False) 
        self.assertEquals(admin_group_access(self.normaluser), False)
        self.assertEquals(admin_group_access(self.sean), True) # In admin group
        self.assertEquals(admin_group_access(self.superuser), True) # 
        

    def test_check_if_is_moderator(self):
        # check_if_is_moderator(tribe, user)
        self.assertEquals(check_if_is_moderator(self.administrators_tribe, self.anonuser), False)
        self.assertEquals(check_if_is_moderator(self.administrators_tribe, self.superuser), True) # In Admin group
        self.assertEquals(check_if_is_moderator(self.administrators_tribe, self.sean), True) # In admin group
        
        # Private group
        self.assertEquals(check_if_is_moderator(self.tribe3, self.sean), True) # In admin group
        self.assertEquals(check_if_is_moderator(self.tribe3, self.anonuser), False) 
        self.assertEquals(check_if_is_moderator(self.tribe3, self.normaluser2), False)
        self.assertEquals(check_if_is_moderator(self.tribe3, self.normaluser), True) # owner, but not moderator
        
        # Open group
        self.assertEquals(check_if_is_moderator(self.tribe1, self.sean), True)
        self.assertEquals(check_if_is_moderator(self.tribe1, self.superuser), True) 
        self.assertEquals(check_if_is_moderator(self.tribe1, self.anonuser), False)
        self.assertEquals(check_if_is_moderator(self.tribe1, self.normaluser), False)
        
    def test_do_403_if_not_superuser(self):
        pass