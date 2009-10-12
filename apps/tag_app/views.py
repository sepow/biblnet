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

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from math import log
# thanks to http://dburke.info/blog/logarithmic-tag-clouds/
from django.views.decorators.cache import cache_page
from django.http import HttpResponseRedirect

def tagcloud(threshold=1, maxsize=2.75, minsize=.70):
    """usage: 
        -threshold: Tag usage less than the threshold is excluded from
            being displayed.  A value of 0 displays all tags.
        -maxsize: max desired CSS font-size in em units
        -minsize: min desired CSS font-size in em units
    
    Returns a list of dictionaries of the tag, its count and
    calculated font-size.
    """
    counts, taglist, tagcloud = [], [], []
    tags = Tag.objects.all()
    if tags: 
        for tag in tags:
            count = tag.items.count()
            count >= threshold and (counts.append(count), taglist.append(tag))
        maxcount = max(counts)
        mincount = min(counts)
        constant = log(maxcount - (mincount - 1))/(maxsize - minsize) or 1
        tagcount = zip(taglist, counts)
        for tag, count in tagcount:
            size = log(count - (mincount - 1))/constant + minsize
            tagcloud.append({'tag': tag, 'count': count, 'size': round(size, 7)})
        return tagcloud
    return None
@cache_page(60 * 60)
def show_tag_cloud(request, template_name="sepow/tagcloud.html" ):
    return render_to_response(template_name, {
    'tag_cloud' : tagcloud()
    }, context_instance=RequestContext(request)
    )
    

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
    

