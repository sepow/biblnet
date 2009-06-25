#-*- coding:utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from tribes.models import TribeMember
from sepow.html import sanitize_html
from datetime import datetime

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

try:
    from friends.models import Friendship
    friends = True
except ImportError:
    friends = False

try:
    from threadedcomments.models import ThreadedComment
    forums = True
except ImportError:
    forums = False

try:
    from wiki.models import Article
    from wiki.views import get_ct
    wiki = True
except ImportError:
    wiki = False

from tribes.models import Tribe
from tribes.forms import *
from microblogging.models import TweetInstance

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM tribes_topic
WHERE tribes_topic.tribe_id = tribes_tribe.id
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM tribes_tribe_members
WHERE tribes_tribe_members.tribe_id = tribes_tribe.id
"""

def has_member(tribe, user):
    if user.is_authenticated():
        if TribeMember.objects.filter(tribe=tribe, user=user).count() > 0:
            return True
    return False


def is_moderator(tribe, user):
    if user.is_authenticated():
        is_in_group = TribeMember.objects.filter(tribe=tribe, user=user)
        if is_in_group:
            return is_in_group[0].moderator
    return False
   

def create(request, form_class=TribeForm, template_name="tribes/create.html"):
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "create":
            tribe_form = form_class(request.POST)
            if tribe_form.is_valid():
                tribe = tribe_form.save(commit=False)
                tribe.creator = request.user
                tribe.save()
                tmember = TribeMember(tribe=tribe, user=request.user)
                tmember.moderator = True
                tmember.save()
                tribe.save()
                if notification:
                    # @@@ might be worth having a shortcut for sending to all users
                    if not tribe.private:
                        notification.send(User.objects.all(), "tribes_new_tribe", {"tribe": tribe}, queue=True)
                        if friends: # @@@ might be worth having a shortcut for sending to all friends
                            notification.send((x['friend'] for x in Friendship.objects.friends_for_user(tribe.creator)), "tribes_friend_tribe", {"tribe": tribe})
                #return render_to_response("base.html", {
                #}, context_instance=RequestContext(request))
                return HttpResponseRedirect(tribe.get_absolute_url())
        else:
            tribe_form = form_class()
    else:
        tribe_form = form_class()
    
    return render_to_response(template_name, {
        "tribe_form": tribe_form,
    }, context_instance=RequestContext(request))

def tribes(request, template_name="tribes/tribes.html", order=None):
    tribes = Tribe.objects.filter(deleted=False, private=False) #TODO skal admins kunne se alle tribes her?
    search_terms = request.GET.get('search', '')
    if search_terms:
        tribes = (tribes.filter(name__icontains=search_terms) |
            tribes.filter(description__icontains=search_terms))
    if order == 'least_topics':
        tribes = tribes.extra(select={'topic_count': TOPIC_COUNT_SQL})
        tribes = tribes.order_by('topic_count')
    elif order == 'most_topics':
        tribes = tribes.extra(select={'topic_count': TOPIC_COUNT_SQL})
        tribes = tribes.order_by('-topic_count')
    elif order == 'least_members':
        tribes = tribes.extra(select={'member_count': MEMBER_COUNT_SQL})
        tribes = tribes.order_by('member_count')
    elif order == 'most_members':
        tribes = tribes.extra(select={'member_count': MEMBER_COUNT_SQL})
        tribes = tribes.order_by('-member_count')
    elif order == 'name_ascending':
        tribes = tribes.order_by('name')
    elif order == 'name_descending':
        tribes = tribes.order_by('-name')
    elif order == 'date_oldest':
        tribes = tribes.order_by('-created')
    elif order == 'date_newest':
        tribes = tribes.order_by('created')

    context = {
        'tribes': tribes,
        'search_terms': search_terms,

    }
    return render_to_response(
        template_name,
        context,
        context_instance=RequestContext(request)
    )

def delete(request, slug, redirect_url=None):
    tribe = get_object_or_404(Tribe, slug=slug)
    if not redirect_url:
        redirect_url = reverse('tribe_list')
    
    # @@@ eventually, we'll remove restriction that tribe.creator can't leave tribe but we'll still require tribe.member_users.all().count() == 1
    if request.user.is_authenticated() and request.method == "POST" and request.user == tribe.creator and tribe.member_users.all().count() == 1:
        tribe.slug = u"%s%s" % ("deleted_", tribe.slug)
        tribe.deleted = True
        tribe.save()
        request.user.message_set.create(message="Tribe %s deleted." % tribe)
        # @@@ no notification as the deleter must be the only member
    
    return HttpResponseRedirect(redirect_url)


def your_tribes(request, template_name="tribes/your_tribes.html"):
    return render_to_response(template_name, {
        "tribes": Tribe.objects.filter(deleted=False, members=request.user).order_by("name"),
    }, context_instance=RequestContext(request))
your_tribes = login_required(your_tribes)

def tribe(request, slug, form_class=TribeUpdateForm,
        template_name="tribes/tribe.html"):
    tribe = get_object_or_404(Tribe, slug=slug)
    

    if tribe.deleted:
        raise Http404
    
    are_member = has_member(tribe, request.user)
    
    if tribe.private and not are_member:
        if not request.user.is_superuser:
            resp = render_to_response('403.html', context_instance=RequestContext(request))
            resp.status_code = 403
            return resp
        
    photos = tribe.photos.all()
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "update" and request.user == tribe.creator:
            tribe_form = form_class(request.POST, instance=tribe)
            if tribe_form.is_valid():
                tribe = tribe_form.save()
        else:
            tribe_form = form_class(instance=tribe)
        if request.POST["action"] == "join" and not tribe.private:
            try: 
                TribeMember.objects.filter(tribe=tribe, user=request.user)[0]
            except:
                tmember = TribeMember(tribe=tribe, user=request.user)
                tmember.save()
                request.user.message_set.create(message="You have joined the tribe %s" % tribe.name)
                if notification:
                    notification.send([tribe.creator], "tribes_created_new_member", {"user": request.user, "tribe": tribe})
                    notification.send(tribe.member_users.all(), "tribes_new_member", {"user": request.user, "tribe": tribe})
                    if friends: # @@@ might be worth having a shortcut for sending to all friends
                        notification.send((x['friend'] for x in Friendship.objects.friends_for_user(request.user)), "tribes_friend_joined", {"user": request.user, "tribe": tribe})
        elif request.POST["action"] == "leave":
            TribeMember.objects.filter(tribe=tribe, user=request.user).delete()

            request.user.message_set.create(message="You have left the tribe %s" % tribe.name)
            if notification:
                pass # @@@
    else:
        tribe_form = form_class(instance=tribe)
    
    topics = tribe.topics.all()[:5] #TODO Skal være de topics der er ændret siden sidst. request.user
    articles = Article.objects.filter(
        content_type=get_ct(tribe),
        object_id=tribe.id).order_by('-last_update')
    total_articles = articles.count()
    articles = articles[:5]
    
    tweets = TweetInstance.objects.tweets_for(tribe).order_by("-sent")
    
    return render_to_response(template_name, {
        "tribe_form": tribe_form,
        "tribe": tribe,
        "photos": photos,
        "topics": topics,
        "articles": articles,
        "tweets": tweets,
        "total_articles": total_articles,
        "are_member": are_member,
        "are_moderator" : is_moderator(tribe, request.user),
    }, context_instance=RequestContext(request))

def topics(request, slug, form_class=TopicForm,
        template_name="tribes/topics.html"):
    tribe = get_object_or_404(Tribe, slug=slug)
    
    if tribe.deleted:
        raise Http404
    
    are_member = has_member(tribe, request.user),
    are_moderator =  is_moderator(tribe, request.user),
    
    if tribe.private and not are_member:
        if not request.user.is_superuser:
            resp = render_to_response('403.html', context_instance=RequestContext(request))
            resp.status_code = 403
            return resp
    else:
        topics = tribe.topics.all()
        
    if request.method == "POST":
        if request.user.is_authenticated():
            if are_member:
                topic_form = form_class(request.POST)
                if topic_form.is_valid():
                    topic = topic_form.save(commit=False)
                    topic.tribe = tribe
                    topic.creator = request.user
                    topic.body = sanitize_html(topic.body)
                    
                    topic.save()        
                    request.user.message_set.create(message="You have started the topic %s" % topic.title)
                    if notification:
                        notification.send(tribe.member_users.all(), "tribes_new_topic", {"topic": topic})
                    topic_form = form_class() # @@@ is this the right way to reset it?
                    return HttpResponseRedirect(topic.get_absolute_url())
            else:
                request.user.message_set.create(message="You are not a member and so cannot start a new topic")
                topic_form = form_class()
        else:
            return HttpResponseForbidden()
    else:
        topic_form = form_class()
    
    return render_to_response(template_name, {
        "topics": topics,
        "tribe": tribe,
        "topic_form": topic_form,
        "are_member": has_member(tribe, request.user),
        "are_moderator" : is_moderator(tribe, request.user),
    }, context_instance=RequestContext(request))


def topic(request, id, edit=False, template_name="tribes/topic.html"):
    topic = get_object_or_404(Topic, id=id)
    
    if topic.tribe.deleted:
        raise Http404
    
    are_member = has_member(topic.tribe, request.user)
    
    if topic.tribe.private and not are_member:
        if not request.user.is_superuser:
            resp = render_to_response('403.html', context_instance=RequestContext(request))
            resp.status_code = 403
            return resp
             
    if request.method == "POST" and edit == True:
        if request.user == topic.creator:
            created = topic.created
            now = datetime.now()
            time_since = now - created
            if time_since.seconds < 60*15:
                topic.body = sanitize_html(request.POST["body"])
                topic.save()
        
        elif is_moderator(topic.tribe, request.user):
                topic.body = sanitize_html(request.POST["body"])
                topic.save()
        
        return HttpResponseRedirect(reverse('tribe_topic', args=[topic.id]))
    topic.views += 1
    topic.save()
    return render_to_response(template_name, {
        'topic': topic,
        'edit': edit,
        'tribe': topic.tribe,
        "are_member": are_member,
        "are_moderator" : is_moderator(topic.tribe, request.user),
    }, context_instance=RequestContext(request))

def topic_delete(request, pk):
    topic = Topic.objects.get(pk=pk)
    
    if topic.tribe.deleted:
        raise Http404
    
    are_member = has_member(topic.tribe, request.user)
    
    if topic.tribe.private and not are_member:
        
        if not request.user.is_superuser:
            resp = render_to_response('403.html', context_instance=RequestContext(request))
            resp.status_code = 403
            return resp
       
    if request.method == "POST" and topic.creator == request.user: 
        if forums:
            ThreadedComment.objects.all_for_object(topic).delete()
        topic.delete()
        
    return HttpResponseRedirect(request.POST["next"])

def topic_moderate(request, pk):
    topic = Topic.objects.get(pk=pk)
    
    if topic.tribe.deleted:
        raise Http404
    are_member = has_member(topic.tribe, request.user)
    
    if topic.tribe.private and not are_member:
        if not request.user.is_superuser:
            resp = render_to_response('403.html', context_instance=RequestContext(request))
            resp.status_code = 403
            return resp

        
    if request.method == "POST" and is_moderator(topic.tribe, request.user):
        if 'sticky' in request.POST:
            if topic.sticky == True:
                topic.sticky = False
            else: 
                topic.sticky = True
            topic.save()
            
        elif 'close' in request.POST:
            if topic.closed == True:
                topic.closed = False
            else: 
                topic.closed = True
            topic.save()          
    return HttpResponseRedirect(request.POST["next"])


