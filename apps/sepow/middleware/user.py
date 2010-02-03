from django.contrib.auth import logout

class CheckIfUserIsActive(object):
    
    def process_request(self, request):
        user = request.user
        
        if not user.is_authenticated():
            return None
        else:
            if not user.is_active:
                logout(request)
        return None
        