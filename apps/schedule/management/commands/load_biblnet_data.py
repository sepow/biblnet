#-*- coding:utf-8 -*-
from django.core.management.base import NoArgsCommand
from django.core.management.color import no_style
from tribes.models import Tribe, TribeMember
from profiles.models import Affiliation, Occupation
from django.contrib.auth.models import User    
from schedule.models import Calendar


superuser = User.objects.get(id=1)

TRIBES = [
          {'name':u'DB - København', u'slug':u'db-kbh', u'creator' : superuser, 
            u'description': u'Danmarks Biblioteksskole Københavns gruppe', u'private': False, 
            u'icon': u'affiliation_db.png',
          }, 
          {'name':u'DB - Aalborg', u'slug':u'db-aalborg', u'creator' : superuser, 
            u'description': u'Danmarks Biblioteksskole Aalborgs gruppe', u'private': False, 
            u'icon': u'affiliation_db.png',
          }, 
          {'name':u'Syddansk Universitet', u'slug':u'sdu', u'creator' : superuser, 
            u'description': u'Syddansk Universitets gruppe', u'private': False, 
            u'icon': u'affiliation_sdu.png',
          }, 
          {'name':u'IT-Universitetet', u'slug':u'it-u', u'creator' : superuser, 
            u'description': u'IT-Universitetets gruppe', u'private': False, 
            u'icon': u'affiliation_itu.png',
          }, 
          {'name':u'Biblioteksforeningen', u'slug':u'bf', u'creator' : superuser, 
            u'description': u'Biblioteksforeningens gruppe', u'private': False, 
            u'icon': u'affiliation_bf.png',
          }, 
          {'name':u'Other organizations', u'slug':u'other', u'creator' : superuser, 
            u'description': u'Other organizations gruppe', u'private': False, 
            u'icon': u'affiliation_external.png',
          }, 
]

OCCUPATION = [
    {u'occupation' : u'Student',
     u'icon': u'occupation_student.png', 
     u'slug':u'student'
    },
    {u'occupation' : u'International student',
     u'icon': u'occupation_international.png',
     u'slug':u'international-student'
    },
    {u'occupation' : u'Former student',
     u'icon': u'occupation_alumni.png',
     u'slug':u'alumni'
    },
    {u'occupation': u'Academic personnel ',
     u'icon': u'occupation_vip.png', 
    u'slug':u'vip'
    },
    {u'occupation': u'Technical or administrative personnel',
     u'icon': u'tap.png', 
    u'slug':u'tap'
    },
    {u'occupation': u'Other',
     u'icon': u'occupation_other.png',
     u'slug':u'other'
    },
]


class Command(NoArgsCommand):
    help = "Load some data into the db"

    def handle_noargs(self, **options):

        tribe = Tribe(name =u'Biblnet', slug =u'biblnet', 
            creator = superuser, description = u'Everybodys favorite tribe',
            private = False )
        tribe.save()
        tm = TribeMember.objects.create(tribe=tribe, user=superuser, moderator=True)
        tm.save()        

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
            icon = "images/affiliateicons/%s" % trie[u'icon']
            af = Affiliation(affiliation=trie['name'], slug=trie['slug'], icon=icon, tribe=tribe)
            af.save()
        
        print "Affiliations and Tribes created"
        for occ in OCCUPATION:
            icon = "images/occupationicons/%s" % occ[u'icon']
            Occupation(occupation = occ[u'occupation'], icon=icon, slug=occ[u'slug']).save()
        
        print "Occupations created"            
        
        from schedule.models import Rule
        try:
            rule = Rule.objects.get(name="Daily")
        except Rule.DoesNotExist:
            rule = Rule(frequency = "YEARLY", name = "Yearly", description = "will recur once every Year")
            rule.save()
            print "YEARLY recurrence created"
            rule = Rule(frequency = "MONTHLY", name = "Monthly", description = "will recur once every Month")
            rule.save()
            print "Monthly recurrence created"
            rule = Rule(frequency = "WEEKLY", name = "Weekly", description = "will recur once every Week")
            rule.save()
            print "Weekly recurrence created"
            rule = Rule(frequency = "DAILY", name = "Daily", description = "will recur once every Day")
            rule.save()
            print "Daily recurrence created"
            print "Rules installed."
