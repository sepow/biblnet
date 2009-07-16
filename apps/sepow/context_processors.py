# -*- coding: utf-8 -*-
from tribes.models import Tribe
def affil_tribe(request):
    if request.user.is_authenticated():
        try:
            affif = {'affil_tribe': request.user.get_profile().affiliation.tribe.get_absolute_url(), }
            return affif
        except AttributeError:
            try: 
                global_tribe = Tribe.objects.get(slug = u'global')
                return {'affil_tribe':global_tribe.get_absolute_url()}
            except:
                pass            
            
    else:
        try: 
            global_tribe = Tribe.objects.get(slug = u'global')
            return {'affil_tribe':global_tribe.get_absolute_url()}
        except:
            pass            
    return {}
