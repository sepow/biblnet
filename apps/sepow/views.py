#-*- coding:utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseServerError
from django_dms.apps.small_dms.models import Document

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context: None
    """
    return render_to_response(template_name,
        context_instance = RequestContext(request)
    )

def list_documents(request, template_name="sepow/list_docs.html"):
    
    return render_to_response(template_name, {
    'documents' : Document.objects.filter(tribe__private=False)
    }, context_instance=RequestContext(request))

def testing(request):
    
    assert False
