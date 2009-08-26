from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

from elsewhere.models import *


@login_required
def example(request):
    if request.method == 'POST':

        new_data = request.POST.copy()
        print new_data
        sn = bool(new_data.get('sn-form') or new_data.get('sn-form.y'))
        im = bool(new_data.get('im-form') or new_data.get('im-form.y'))
        w = bool(new_data.get('w-form') or new_data.get('w-form.y'))
        
        d_sn = bool(new_data.get('delete-sn-form') or new_data.get('delete-sn-form.y') == 0 or new_data.get('delete-sn-form.y'))
        d_im = bool(new_data.get('delete-im-form') or new_data.get('delete-im-form.y') == 0 or new_data.get('delete-im-form.y'))
        d_w = bool(new_data.get('delete-w-form') or new_data.get('delete-w-form.y') == 0 or  new_data.get('delete-w-form.y'))

        print sn, im, w  
   
        if sn or im or w:

            if sn:
                form = SocialNetworkForm(request.POST)
            elif im:
                form = InstantMessengerForm(request.POST)
            elif w:
                form = WebsiteForm(request.POST)

            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                return HttpResponseRedirect(request.path)
            else:
                ## TODO should probably show the errors
                print form.errors

    
        else:
            try: 
                delete_id = request.POST['delete_id']

                if d_sn:
                    request.user.social_network_profiles.get(id=delete_id).delete()
                elif d_im:
                    request.user.instant_messenger_profiles.get(id=delete_id).delete()
                elif d_w:
                    request.user.website_profiles.get(id=delete_id).delete()

                return HttpResponseRedirect(request.path)
            except:
                pass
    # Create blank forms
    sn_form = SocialNetworkForm()
    im_form = InstantMessengerForm()
    w_form = WebsiteForm()

    return render_to_response('elsewhere/base.html', {
        'sn_form': sn_form, 'im_form': im_form, 'w_form': w_form,
    }, context_instance=RequestContext(request))
