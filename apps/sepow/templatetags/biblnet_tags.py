from django import template
from tribes.models import Tribe
from datetime import datetime
from tribes.models import TribeMember
from threadedcomments.models import ThreadedComment
from tribes.models import Topic

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
        for topic in modified_topics:
            new_posts += ThreadedComment.objects.filter(date_modified__gte=since, object_id=topic.id).count() # user != user

    if new_topics or new_posts:
        changed = True
    else:
        changed = False

    return {
        'changed' : changed, 
        'tribe' : tribe,
        'new_topics': new_topics, 
        'new_posts': new_posts, 
    }
    
register.inclusion_tag('sepow/new_since_last_visit.html')(new_since_last_visit)


def visit_tribe(tribe, user):
    if has_member(tribe, user): # if the user is a member, set the last visit to to now
        try:
            tribe_member = TribeMember.objects.filter(tribe=tribe, user=user)[0]
            tribe_member.last_visit = datetime.now()
            tribe_member.save()
        except AttributeError:
            pass
    return ""
register.simple_tag(visit_tribe)

