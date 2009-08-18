#-*- coding:utf-8 -*-
from django.core.management.base import NoArgsCommand
from tribes.models import Tribe, TribeMember
from profiles.models import Affiliation, Occupation
from django.contrib.auth.models import User    
from schedule.models import Calendar


superuser = User.objects.get(id=1)

TRIBES = [
          {'name':u'DB - København', u'slug':u'db-kbh', u'creator' : superuser, 
            u'description': u'Danmarks Biblioteksskole Københavns gruppe', u'private': False, 
            u'icon': u'./Affiliation/affiliation_db.png',
          }, 
          {'name':u'DB - Aalborg', u'slug':u'db-aalborg', u'creator' : superuser, 
            u'description': u'Danmarks Biblioteksskole Aalborgs gruppe', u'private': False, 
            u'icon': u'./Affiliation/affiliation_db.png',
          }, 
          {'name':u'Syddansk Universitet', u'slug':u'sdu', u'creator' : superuser, 
            u'description': u'Syddansk Universitets gruppe', u'private': False, 
            u'icon': u'./Affiliation/affiliation_sdu.png',
          }, 
          {'name':u'IT-Universitetet', u'slug':u'it-u', u'creator' : superuser, 
            u'description': u'IT-Universitetets gruppe', u'private': False, 
            u'icon': u'./Affiliation/affiliation_itu.png',
          }, 
          {'name':u'Biblioteksforeningen', u'slug':u'bf', u'creator' : superuser, 
            u'description': u'Biblioteksforeningens gruppe', u'private': False, 
            u'icon': u'./Affiliation/affiliation_bf.png',
          }, 
          {'name':u'Other organizations', u'slug':u'other', u'creator' : superuser, 
            u'description': u'Other organizations gruppe', u'private': False, 
            u'icon': u'./Affiliation/affiliation_external.png',
          }, 
]

OCCUPATION = [
    {u'occupation' : u'Student',
     u'icon': u'./Occupation/occupation_student.png', 
     u'slug':u'student'
    },
    {u'occupation' : u'International student',
     u'icon': u'./Occupation/occupation_international.png',
     u'slug':u'international-student'
    },
    {u'occupation' : u'Former student',
     u'icon': u'./Occupation/occupation_alumni.png',
     u'slug':u'alumni'
    },
    {u'occupation': u'Academic personnel ',
     u'icon': u'./Occupation/occupation_vip.png', 
    u'slug':u'vip'
    },
    {u'occupation': u'Technical or administrative personnel',
     u'icon': u'./Occupation/tap.png', 
    u'slug':u'tap'
    },
    {u'occupation': u'Other',
     u'icon': u'./Occupation/occupation_other.png',
     u'slug':u'other'
    },
]


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        for trie in TRIBES:
            
            tribe = Tribe(name = trie['name'], slug = trie['slug'], 
            creator = trie['creator'], description = trie['description'],
            private = trie['private'] )
            
            tribe.save()
            tm = TribeMember.objects.create(tribe=tribe, user=trie['creator'], moderator=True)
            tm.save()        
            
            tribe_cal = Calendar.objects.get_or_create_calendar_for_object(tribe, name = "%s" % tribe,)
            tribe_cal.slug = tribe.slug
            tribe_cal.save() 

            af = Affiliation(affiliation=trie['name'], slug=trie['slug'], icon=trie['icon'], tribe=tribe)
            af.save()
        for occ in OCCUPATION:
            Occupation(occupation = occ[u'occupation'], icon=occ[u'icon'], slug=occ[u'slug']).save()
