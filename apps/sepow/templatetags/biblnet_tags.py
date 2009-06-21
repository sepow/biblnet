from django import template
from tribes.models import Tribe
from datetime import datetime

register = template.Library()

def new_since_last_visit(tribe, user='user'):
    # since = TribeMember.objects.filter(tribe=tribe, user=user)[0].last_visit()
    new_topics = tribe.topics.filter(created__gte=datetime.now()).count() # Tribe.topics.objects.filter(created>datetime.now()).count()
    new_posts = 0 # new posts 
    return {
        'tribe' : tribe,
        'new_topics': new_topics, 
        'new_posts': new_posts, 
    }
    
register.inclusion_tag('sepow/new_since_last_visit.html')(new_since_last_visit)
