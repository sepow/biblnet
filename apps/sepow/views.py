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


def testing(request):

    from tagging.models import Tag, TaggedItem
    
    tags = ["asd"]
    
    query_tags = Tag.objects.filter(name__in=tags)
    from tribes.models import Tribe 
    from photos.models import Image
    from bookmarks.models import BookmarkInstance
    from django_dms.apps.small_dms.models import Document
    from tribes.models import Topic as TribeTopic
    from wiki.models import Article as WikiArticle
    from django.contrib.contenttypes.models import ContentType

    
    
    def get_not_deleted_tribe_wikies():
        deleted_tribes = Tribe.objects.filter(deleted=True)
        ctype_tribe = ContentType.objects.get(name="tribe")
        return  WikiArticle.objects.all().filter(content_type=ctype_tribe).exclude(object_id__in=deleted_tribes)
    
    query = (
       ("phototags", Image.objects.all()),
       ("bookmarktags", BookmarkInstance.objects.all()),
       ("tribe_tags", Tribe.objects.all().filter(deleted=False)),
       ("tribe_topic_tags", TribeTopic.objects.all().filter(tribe__deleted=False)),
       ("wiki_article_tags", get_not_deleted_tribe_wikies()),
       ("document_tags", Document.objects.all().filter(tribe__deleted=False)),
       )
    
    for name, thing in query:
        print name, TaggedItem.objects.get_intersection_by_model(thing, query_tags)
    
    assert False
