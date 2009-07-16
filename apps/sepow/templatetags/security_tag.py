from django import template
from tribes.models import TribeMember
register = template.Library()

def has_member(tribe, user):
    if user.is_authenticated():
        if TribeMember.objects.filter(tribe=tribe, user=user).count() > 0:
            return True
    return False

def is_moderator(tribe, user):
    if user.is_authenticated():
        is_in_group = TribeMember.objects.filter(tribe=tribe, user=user)
        if is_in_group:
            return is_in_group[0].moderator
    return False

def comments(context, obj):
    return {
        'object': obj, 
        'request': context['request'],
        'user': context['user'],
        "are_member": has_member(obj.tribe, context['request'].user),
        "are_moderator" : is_moderator(obj.tribe, context['request'].user),
    }

register.inclusion_tag('threadedcomments/comments.html', takes_context=True)(comments)

'''
from tribes.models import Tribe, Topic
from wiki.models import Article
from threadedcomment.models import Comment


def get_tribe_from_object(obj):
    # takes an object, and returns the tribe is belongs to
    if isinstance(obj, Tribe):
        return obj
    elif isinstance(obj, Wiki):
        return obj.group
    elif isinstance(obj, Comment):
        return obj # HUR?
    elif isinstance(obj, Topic):
        return obj.tribe
    else: 
        return False


def can_access(obj, user):
    # Returns true if the user can access object
    pass
'''
