from django.http import HttpResponse, HttpResponseForbidden

# @@@ these can be cleaned up a lot, made more generic and with better queries

def username_autocomplete_all(request):
    if request.user.is_authenticated():
        from django.contrib.auth.models import User
        from basic_profiles.models import Profile
        from avatar.templatetags.avatar_tags import avatar
        q = request.GET.get("q")
        users = User.objects.all()
        content = []
        # @@@ temporary hack -- don't try this at home (or on real sites)
        for user in users:
            if user.username.lower().startswith(q):
                try:
                    profile = user.get_profile()
                    entry = "%s,,%s,,%s" % (
                        avatar(user, 40),
                        user.username,
                        profile.location
                    )
                except Profile.DoesNotExist:
                    pass
                content.append(entry)
        response = HttpResponse("\n".join(content))
    else:
        response = HttpResponseForbidden()
    setattr(response, "djangologging.suppress_output", True)
    return response


def username_autocomplete_friends(request):
    from django.contrib.auth.models import User
    from avatar.templatetags.avatar_tags import avatar
    
    if request.user.is_authenticated():
        results = []
        q = request.GET['q']
        
        def create_entry(user):
            return "%s,,%s,,%s" % ( avatar(user, 40), user.username, user.get_profile().name)
        
        if len(q) > 1:
            users = User.objects.all().filter(is_active=True)
            model_results = users.filter(profile__name__icontains=q) | users.filter(profile__user__username__icontains=q)
            results = [create_entry(x) for x in model_results] 
        
        response = HttpResponse("\n".join(results[:10]))
    else:
        response = HttpResponseForbidden()
    
    setattr(response, "djangologging.suppress_output", True)
    return response