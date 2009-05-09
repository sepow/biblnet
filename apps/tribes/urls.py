from django.conf.urls.defaults import *

from tribes.models import Tribe
from wiki import models as wiki_models

wiki_args = {'group_slug_field': 'slug',
             'group_qs': Tribe.objects.filter(deleted=False)}


                

urlpatterns = \
    patterns('',
        url(r'^create/$', 'tribes.views.create', name="tribe_create"),
        url(r'^your_tribes/$', 'tribes.views.your_tribes', name="your_tribes"),
        
        url(r'^$', 'tribes.views.tribes', name="tribe_list"),
        url(r'^order/topics/least-topics/$', 'tribes.views.tribes',
            {'order': 'least_topics'}, name="tribe_list_least_topics"),
        url(r'^order/topics/most-topics/$', 'tribes.views.tribes',
            {'order': 'most_topics'}, name="tribe_list_most_topics"),
        url(r'^order/members/least-members/$', 'tribes.views.tribes',
            {'order': 'least_members'}, name="tribe_list_least_members"),
        url(r'^order/members/most-members/$', 'tribes.views.tribes',
            {'order': 'most_members'}, name="tribe_list_most_members"),
        url(r'^order/name/ascending/$', 'tribes.views.tribes',
            {'order': 'name_ascending'}, name="tribe_list_name_ascending"),
        url(r'^order/name/descending/$', 'tribes.views.tribes',
            {'order': 'name_descending'}, name="tribe_list_name_descending"),
        url(r'^order/date/oldest/$', 'tribes.views.tribes',
            {'order': 'date_oldest'}, name="tribe_list_date_oldest"),
        url(r'^order/date/newest/$', 'tribes.views.tribes',
            {'order': 'date_newest'}, name="tribe_list_date_newest"),
        
        # tribe-specific
        url(r'^tribe/([-\w]+)/$', 'tribes.views.tribe', name="tribe_detail"),
        url(r'^tribe/([-\w]+)/delete/$', 'tribes.views.delete', name="tribe_delete"),
        url(r'^tribe/([-\w]+)/members/$', 'tribes.views.tribe', {"template_name":"tribes/tribe_members.html"}, name="tribe_members"),
        url(r'^tribe/([-\w]+)/admin/$', 'tribes.views.tribe', {"template_name":"tribes/tribe_admin.html"}, name="tribe_admin"),
        
        # topics
        url(r'^tribe/([-\w]+)/topics/$', 'tribes.views.topics', name="tribe_topics"),
        url(r'^topic/(\d+)/edit/$', 'tribes.views.topic', kwargs={"edit": True}, name="tribe_topic_edit"),
        url(r'^topic/(\d+)/delete/$', 'tribes.views.topic_delete', name="tribe_topic_delete"), #TODO virker ikke... 
        url(r'^topic/(\d+)/reply/$', 'tribes.views.topic', {"template_name":"tribes/add_post.html"} , name="tribe_reply"),
        # TODO  url(r'^topic/(\d+)/move/$',
        url(r'^topic/(\d+)/$', 'tribes.views.topic', name="tribe_topic"),
        
        # wiki
        url(r'^tribe/(?P<group_slug>\w+)/wiki/', include('wiki.urls'), kwargs=wiki_args),
    )
