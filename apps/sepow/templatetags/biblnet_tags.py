from django import template
from tribes.models import Tribe
from datetime import datetime
from tribes.models import TribeMember
from threadedcomments.models import ThreadedComment
from tribes.models import Topic
from django.contrib.auth.models import User
from schedule.utils import EventListManager
from schedule.models import Calendar, Event

from django_dms.apps.small_dms.models import Document
from apps.wiki.models import Article # from wiki.models import Article <- virker ikke! apps.wiki.models virker.. wtf
register = template.Library()


##
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
import re

register = template.Library()

@register.filter
@stringfilter
def mungify(email, text=None, autoescape=None):
    text = text or email
    
    if autoescape:
        email = conditional_escape(email)
        text = conditional_escape(text)

    emailArrayContent = ''
    textArrayContent = ''
    r = lambda c: '"' + str(ord(c)) + '",'

    for c in email: emailArrayContent += r(c)
    for c in text: textArrayContent += r(c)

    result = """<script>
                var _tyjsdf = [%s], _qplmks = [%s];
                document.write('<a href="&#x6d;&#97;&#105;&#x6c;&#000116;&#111;&#x3a;');
                for(_i=0;_i<_tyjsdf.length;_i++){document.write('&#'+_tyjsdf[_i]+';');}
                document.write('">');
                for(_i=0;_i<_qplmks.length;_i++){document.write('&#'+_qplmks[_i]+';');}
                document.write('</a>');
                </script>""" % (re.sub(r',$', '', emailArrayContent),
                                re.sub(r',$', '', textArrayContent))
    
    return mark_safe(result)

mungify.needs_autoescape = True
## 
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
        new_wiki = tribe.wiki_articles().filter(created_at__gte=since).count()
        new_docs = Document.objects.filter(tribe=tribe).filter(date_added__gte=since).count()
        
    changed = bool(new_topics or new_posts or new_docs or new_wiki)
    return {
        'changed' : changed,
        'tribe' : tribe,
        'new_topics' : new_topics,
        'new_posts' : new_posts,
        'new_docs' : new_docs,
        'new_wiki' : new_wiki,
    }
register.inclusion_tag('sepow/new_since_last_visit.html')(new_since_last_visit)

def new_tribes_since_last_visit(user):
    since = user.get_profile().last_visit
    new_tribes = Tribe.objects.filter(created__gte=since, private=False).count()
    return {'count' : new_tribes, }
register.inclusion_tag('sepow/new_tribes_since_last_visit.html')(new_tribes_since_last_visit)

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

def profile_stats(user): # I should cache this I guess
    wiki = Article.objects.filter(creator=user).count()
    documents = Document.objects.filter(uploader=user).count()
    topics = Topic.objects.filter(creator=user).count()
    comments = ThreadedComment.objects.filter(user=user).count()

    latest_topic = None
    latest_comment = None
    if comments:
        latest_comment = ThreadedComment.objects.filter(user=user).latest()
    if topics:
        latest_topic = Topic.objects.filter(creator=user).latest()
    last_login = user.get_profile().last_visit_storage

    return {'wiki' : wiki,
            'documents' : documents,
            'topics' : topics,
            'comments' : comments,
            'latest_comment' : latest_comment,
            'last_login' : last_login,
            'latest_topic' : latest_topic,
           }
    
register.inclusion_tag('profiles/profile_stats.html')(profile_stats)
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


