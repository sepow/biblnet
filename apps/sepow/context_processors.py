# -*- coding: utf-8 -*-
from tribes.models import Tribe


def affil_tribe(request):
    if request.user.is_authenticated():
        try: # try to find the tribe the user is affiliated with. 
            affif = {'affil_tribe': request.user.get_profile().affiliation.tribe.get_absolute_url(), }
            return affif
        except AttributeError:
            pass           

    try: # if that doesn't work, try to find a global tribe. 
        global_tribe = Tribe.objects.get(slug = u'biblnet')
        return {'affil_tribe' : global_tribe.get_absolute_url()}
    except:
        pass            
    
    return {}