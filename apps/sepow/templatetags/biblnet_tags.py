from django import template
from tribes.models import Tribe
from datetime import datetime
from tribes.models import TribeMember
from threadedcomments.models import ThreadedComment
from tribes.models import Topic
from django.contrib.auth.models import User
from schedule.utils import EventListManager
from schedule.models import Calendar, Event
# from wiki.models import Article <- virker ikke! apps.wiki.models virker.. wtf
from django_dms.apps.small_dms.models import Document

register = template.Library()

def has_member(tribe, user):
    if user.is_authenticated():
        if TribeMember.objects.filter(tribe=tribe, user=user).count() > 0:
            return True
    return False
    
def new_since_last_visit(tribe, user):
    if has_member(tribe, user):
        
        since = TribeMember.objects.filter(tribe=tribe, user=user)[0].last_visit
        
        # new topics
        new_topics = tribe.topics.filter(created__gte=since).count() # user != user
        
        # new posts
        modified_topics = tribe.topics.filter(modified__gte=since) 
        new_posts = 0        
        if modified_topics: 
            new_posts = ThreadedComment.objects.filter(object_id__in=modified_topics, date_modified__gte=since).count()
        new_wiki = 0
        new_docs = Document.objects.filter(tribe=tribe).filter(date_added__gte=since).count()
        
    changed = bool(new_topics or new_posts or new_docs)
    return {
        'changed' : changed,
        'tribe' : tribe,
        'new_topics' : new_topics,
        'new_posts' : new_posts,
        'new_docs' : new_docs,
    }
register.inclusion_tag('sepow/new_since_last_visit.html')(new_since_last_visit)


def visit_tribe(tribe, user):
    if has_member(tribe, user): # if the user is a member, set the last visit to to now
        try:
            tribe_member = TribeMember.objects.get(tribe=tribe, user=user)
            tribe_member.last_visit = datetime.now()
            tribe_member.save()
        except AttributeError:
            pass
    return ""
register.simple_tag(visit_tribe)

import itertools 
def get_tribe_calendar(tribe, user, event_slice=5):
    '''
    Returns the next events for the user from one tribe. 
    
    Yields a itertools.islice
    '''  
    events = None
    try:
        calendar = Calendar.objects.get_calendar_for_object(tribe)
        events = itertools.islice(calendar.occurrences_after(date=datetime.now()), event_slice)
    except: 
        pass
    #user.message_set.create(message="Type: %s" % type(events))   
    return {
    'events' : events
    }
    
register.inclusion_tag('sepow/get_tribe_calendar.html')(get_tribe_calendar)

def get_all_tribe_calendars(user, event_slice=5):
    '''
    Returns the users next events, gathered from all the tribes he is a member of. 
    
    Yields a itertools.islice
    '''  
    events = None
    tribes = user.tribe_set.all()
    
    try:
        events = Event.objects.filter(calendar__calendarrelation__object_id__in=tribes)
        events = itertools.islice(EventListManager(events).occurrences_after(datetime.now()), event_slice)
    except:
        pass

    return {
    'events' : events,
    }
    
register.inclusion_tag('sepow/get_tribe_calendar.html')(get_all_tribe_calendars)


def get_latest(users=8, topics=1, comments=2):
    '''
    Returns 3 different lists.
    
    latest_users  - a list of latest users to visit the site.
    latest_topics - the latest public topics to be created.
    latest_posts  - the latest public replies to a topic. 
    
    '''  
    
    try:
        latest_topic = Topic.objects.filter(tribe__private=False).filter(tribe__deleted=False).order_by('-created')[:topics]
    except IndexError:
        latest_topic = None

    try:
        # find the lates topic that's been modified in a public tribe' TODO Cache this?
        last_modified = Topic.objects.filter(tribe__private=False).filter(tribe__deleted=False).order_by('-modified')
        latest_post = ThreadedComment.objects.filter(object_id__in=last_modified).order_by('-date_modified')[:comments]
    except IndexError:
        latest_post = None

    return {'latest_users' : User.objects.order_by('-profile__last_visit_storage')[:users],
            'latest_topics' : latest_topic,
            'latest_posts'  : latest_post,
            }

register.inclusion_tag('sepow/latest_updates.html')(get_latest)


@register.filter("truncate_chars")
def truncate_chars(value, max_length):
    '''
    if len(value) > max_length:
        truncd_val = value[:max_length]
        if value[max_length+1] != " ":
            truncd_val = truncd_val[:truncd_val.rfind(" ")]
        return  truncd_val + "..."
    '''
    return value


