from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


from tagging.models import Tag, TaggedItem
from photos.models import Image
from bookmarks.models import BookmarkInstance

from projects.models import Topic as ProjectTopic

from tribes.models import Tribe
from tribes.models import Topic as TribeTopic
from django_dms.apps.small_dms.models import Document 
from wiki.models import Article as WikiArticle

def tags(request, tag, template_name='tags/index.html'):
    tag = get_object_or_404(Tag, name=tag)
    

    
    phototags = TaggedItem.objects.get_by_model(Image, tag)
    bookmarktags = TaggedItem.objects.get_by_model(BookmarkInstance, tag)

    tribe_tags = TaggedItem.objects.get_by_model(Tribe, tag).filter(deleted=False)
    tribe_topic_tags = TaggedItem.objects.get_by_model(TribeTopic, tag).filter(tribe__deleted=False)
    
    # @@@ TODO: tribe_wiki_article_tags and project_wiki_article_tags
    wiki_article_tags = TaggedItem.objects.get_by_model(WikiArticle, tag)
    
    document_tags = TaggedItem.objects.get_by_model(Document, tag).filter(tribe__deleted=False).filter(tribe__private=False)
    
    return render_to_response(template_name, {
        'tag': tag,
        'phototags': phototags,
        'bookmarktags': bookmarktags,
        'tribe_tags': tribe_tags,
        'tribe_topic_tags': tribe_topic_tags,
        'wiki_article_tags': wiki_article_tags,
        'document_tags' : document_tags,
    }, context_instance=RequestContext(request))
