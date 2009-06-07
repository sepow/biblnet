# -*- coding: utf-8 -*-

def affil_tribe(request):
    if request.user.is_authenticated():
        try:
            affif = {'affil_tribe': request.user.get_profile().affiliation.tribe.get_absolute_url(), }
            return affif
        except AttributeError:
            return {}
    else:
        return {}
