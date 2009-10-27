#-*- coding:utf-8 -*-
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

from django.db.models import Q
def testing(request):
    
    from tagging.models import Tag, TaggedItem
    
    tags = ["asd", "poop"]
    query_tags = Tag.objects.filter(name__in=tags)
    from tribes.models import Topic 
    print TaggedItem.objects.get_intersection_by_model(Topic.objects.all(), query_tags)
    # dette skal så gøres for alle modeller..
    assert False
