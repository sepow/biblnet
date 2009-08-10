from django import template
from apps.wiki.models import Article
from tribes.models import TribeMember
from tribes.models import Tribe, Topic
from threadedcomments.models import ThreadedComment
from django_dms.apps.small_dms.models import Document
from schedule.models import Calendar, Event, Occurrence


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
        'tribe' : obj.tribe,
        'object': obj, 
        'request': context['request'],
        'user': context['user'],
        "are_member": has_member(obj.tribe, context['request'].user),
        "are_moderator" : is_moderator(obj.tribe, context['request'].user),
    }

register.inclusion_tag('threadedcomments/comments.html', takes_context=True)(comments)



def get_tribe_from_object(obj):
    # print "object: ", obj
    if isinstance(obj, Tribe):
        return obj
    elif isinstance(obj, ThreadedComment):
        return obj.get_content_object().tribe
    elif isinstance(obj, Document):
        return obj.tribe
    elif isinstance(obj, Topic):
        return obj.tribe
    elif isinstance(obj, Event):
        return obj.calendar.calendarrelation_set.all()[0].content_object   
    elif isinstance(obj, Occurrence):
        return obj.event.calendar.calendarrelation_set.all()[0].content_object   
    elif isinstance(obj, Calendar):
        return obj.calendarrelation_set.all()[0].content_object   
    elif isinstance(obj, Article):
        return obj.group
    else: 
        return None

register.simple_tag(get_tribe_from_object)

def can_access(obj, user):
    tribe = get_tribe_from_object(obj)
    data = {'can_access' : has_member(tribe, user)}
    if tribe:
        data['tribe'] = tribe
    return data



class CanAccessNode(template.Node):
    def __init__(self, obj, user):
        self.obj = template.Variable(obj)
        self.user = template.Variable(user)
    def render(self, context):
        try:
            actual_obj = self.obj.resolve(context)
            actual_user = self.user.resolve(context)
            
            tribe = get_tribe_from_object(actual_obj)
            user_can_access = False
            
            if tribe:
                user_can_access = (has_member(tribe, actual_user) or not tribe.private)
            # print "Tribe: ", tribe
            # print "Can access?: ", user_can_access
            context['tribe'] = tribe
            context['has_access'] = user_can_access
            
        except template.VariableDoesNotExist:
            return ''
        return ''

def do_can_access(parser, token):
    ''' 
    Takes an object and a user, and determins if the object belongs to a tribe
    and if so, if the user can access this object/tribe
    
    returns:
    
    'tribe' which is the tribe or None
    'has_access' which is a bool determining if the object should be shown. 
    '''
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, obj, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return CanAccessNode(obj, user)

register.tag('can_access', do_can_access)

