from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from tagging.models import Tag
from math import log
# thanks to http://dburke.info/blog/logarithmic-tag-clouds/
from django.views.decorators.cache import cache_page
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

@cache_page(60 * 60)
def show_tag_cloud(request, template_name="sepow/tagcloud.html" ):
    return render_to_response(template_name, {
    'tag_cloud' : tagcloud()
    }, context_instance=RequestContext(request)
    )
    
