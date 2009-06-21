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



