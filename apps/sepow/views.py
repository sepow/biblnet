from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseServerError

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    return render_to_response(template_name,
        context_instance = RequestContext(request)
    )

from django.core.serializers import serialize
from django.contrib.auth.models import User 

def testing(request):
    q = request.GET['q']
    city_list = User.objects.filter(username__istartswith=q).order_by("username")[:10]
    json = serialize("json", city_list)

    return HttpResponse(json, mimetype="application/x-javascript")
