from django.views.debug import technical_500_response
import sys
from django.contrib.auth import logout


class UserBasedExceptionMiddleware(object):
    def process_exception(self, request, exception):
        if request.user.is_superuser:
            return technical_500_response(request, *sys.exc_info())

class CheckIfUserIsActive(object):
    
    def process_request(self, request):
        user = request.user
        
        if not user.is_authenticated():
            return None
        else:
            if not user.is_active:
                logout(request)
        return None
        