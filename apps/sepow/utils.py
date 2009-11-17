# -*- coding: utf-8 -*-
from django.conf import settings
from tribes.models import Tribe, TribeMember
from django.shortcuts import render_to_response
from django.template.context import RequestContext


def admin_group_access(user):
    # Returns true if the user is a superuser, of is she is a member of the admin tribe

    admin_group_name = getattr(settings, 'ADMIN_GROUP_NAME', 'Administrators')
    admin_tribe = Tribe.objects.get(name=admin_group_name)
    try:
        tm = TribeMember.objects.get(tribe=admin_tribe, user=user)
        return True
    except TribeMember.DoesNotExist:
        if user.is_superuser:
            return True
    return False
    
    
def check_if_is_moderator(tribe, user):
    if user.is_authenticated():
        if admin_group_access(user):
            return True
        is_in_group = TribeMember.objects.filter(tribe=tribe, user=user)
        if is_in_group:
            return is_in_group[0].moderator
    return False

def do_403_if_not_superuser(request):
    if not admin_group_access(request.user):
        resp = render_to_response('403.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp
    else:
        return False