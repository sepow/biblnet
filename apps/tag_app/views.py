from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


from tagging.models import Tag, TaggedItem
from photos.models import Image
from bookmarks.models import BookmarkInstance
from tribes.models import Tribe
from tribes.models import Topic as TribeTopic
from django_dms.apps.small_dms.models import Document 
from wiki.models import Article as WikiArticle
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from math import log
# thanks to http://dburke.info/blog/logarithmic-tag-clouds/
from django.views.decorators.cache import cache_page
from django.http import HttpResponseRedirect
from tag_app.forms import CombineTagsForm
from tagging.utils import get_tag_list
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
    wiki_article_tags = TaggedItem.objects.get_by_model(WikiArticle, tag)
    document_tags = TaggedItem.objects.get_by_model(Document, tag).filter(tribe__deleted=False)
    
    return render_to_response(template_name, {
        'tag': tag,
        'phototags': phototags,
        'bookmarktags': bookmarktags,
        'tribe_tags': tribe_tags,
        'tribe_topic_tags': tribe_topic_tags,
        'wiki_article_tags': wiki_article_tags,
        'document_tags' : document_tags,
    }, context_instance=RequestContext(request))
    
def combine_tags(request, template_name="tags/combine.html", form_class=CombineTagsForm):
    
    def get_not_deleted_tribe_wikies():
        deleted_tribes = Tribe.objects.filter(deleted=True)
        ctype_tribe = ContentType.objects.get(name="tribe")
        return  WikiArticle.objects.all().filter(content_type=ctype_tribe).exclude(object_id__in=deleted_tribes)
    
    # @todo: cache det her 
    query = (
       ("phototags", Image.objects.all()),
       ("bookmarktags", BookmarkInstance.objects.all()),
       ("tribe_tags", Tribe.objects.all().filter(deleted=False)),
       ("tribe_topic_tags", TribeTopic.objects.all().filter(tribe__deleted=False)),
       ("wiki_article_tags", get_not_deleted_tribe_wikies()),
       ("document_tags", Document.objects.all().filter(tribe__deleted=False)),
       )
    
    tags = []

    if request.method == "POST":
        
        combine_form = form_class(request.POST)
        
        if combine_form.is_valid():
            return_dict = {}
            tags = combine_form.cleaned_data['tags']
            
            if request.POST["bool"] == "AND":
                if len(get_tag_list(tags)) == len(tags):
                    
                    # If all of the userinput tags are valid tags, then there's a 
                    # point in searching for objects that contain them all.
                    # Otherwise only the excisting tags would be used when 
                    # comparing.
                     
                    for name, thing in query:
                        return_dict[name] = TaggedItem.objects.get_intersection_by_model(thing, tags)
            elif request.POST["bool"] == "OR": # If either of the tags..
                for name, thing in query:
                    return_dict[name] = TaggedItem.objects.get_union_by_model(thing, tags)
            
            return_dict.update({
                "form": combine_form,
                "tags": tags,
            })
            
            return render_to_response(template_name, return_dict, context_instance=RequestContext(request))            
    else:
        combine_form = form_class()

    return render_to_response(template_name, {
        "form": combine_form,
        "tags": tags,
    }, context_instance=RequestContext(request))