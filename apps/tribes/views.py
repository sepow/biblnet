#-*- coding:utf-8 -*-
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
from schedule.models import Calendar
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django_dms.apps.small_dms.models import Document
from sepow.utils import admin_group_access, check_if_is_moderator, do_403_if_not_superuser
from messages.models import Message
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

TOPIC_COUNT_SQL = """
SELECT COUNT(*)
FROM tribes_topic
WHERE tribes_topic.tribe_id = tribes_tribe.id
"""
MEMBER_COUNT_SQL = """
SELECT COUNT(*)
FROM tribes_tribemember
WHERE tribes_tribemember.tribe_id = tribes_tribe.id
"""

def has_member(tribe, user):
    if user.is_authenticated():
        if TribeMember.objects.filter(tribe=tribe, user=user).count() > 0:
            return True
        elif admin_group_access(user):
            return True
    return False


def is_moderator(tribe, user):
    return check_if_is_moderator(tribe, user)
   
@login_required
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
                # Calendar
                tribe_cal = Calendar.objects.get_or_create_calendar_for_object(tribe, name = "%s" % tribe,)
                tribe_cal.slug = tribe.slug
                tribe_cal.save()
                         
                if notification:
                    # @@@ might be worth having a shortcut for sending to all users
                    if not tribe.private:
                        notification.send(User.objects.all(), "tribes_new_tribe", {"tribe": tribe}, queue=True)
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
        tribes = tribes.order_by('created')
    elif order == 'date_newest':
        tribes = tribes.order_by('-created')

    context = {
        'tribes': tribes,
        'search_terms': search_terms,
        'order': order,
    }
    return render_to_response(
        template_name,
        context,
        context_instance=RequestContext(request)
    )

@login_required
def delete(request, slug, redirect_url=None):
    tribe = get_object_or_404(Tribe, slug=slug)
    if not redirect_url:
        redirect_url = reverse('tribe_list')
    
    # @@@ eventually, we'll remove restriction that tribe.creator can't leave tribe but we'll still require tribe.member_users.all().count() == 1
    if request.user.is_authenticated() and request.method == "POST" and request.user == tribe.creator and tribe.member_users.all().count() == 1:
        from profiles.models import Affiliation
        if not Affiliation.objects.filter(tribe=tribe):
            try:
                request.user.message_set.create(message=ugettext("Tribe %s deleted.") % tribe)
                deleted = datetime.now().strftime("%s__")
                tribe.slug = u"%s%s" % (deleted, tribe.slug)
                tribe.name = u"%s%s" % (deleted, tribe.name)
                tribe.deleted = True
                tribe.save()
                
                calendar = Calendar.objects.get_calendar_for_object(tribe)
                calendar.name = u"%s%s" % (deleted, calendar.name)
                calendar.slug = u"%s%s" % (deleted, calendar.slug)
                calendar.save()
                
            except:
                request.user.message_set.create(message=ugettext("Something bad happend as we tried to delete your tribe, please contact your Admin"))
        else:
            request.user.message_set.create(message=ugettext("Tribe %s cannot be deleted. It is an Affiliation tribe") % tribe)
    
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
        access = do_403_if_not_superuser(request)
        if access: 
            return access
        
    photos = tribe.photos.all()
    
    if request.user.is_authenticated() and request.method == "POST":
        if request.POST["action"] == "update" and (request.user == tribe.creator or request.user.is_superuser):
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
                    #notification.send([tribe.creator], "tribes_created_new_member", {"user": request.user, "tribe": tribe})
                    notification.send(tribe.member_users.all(), "tribes_new_member", {"user": request.user, "tribe": tribe})
        elif request.POST["action"] == "leave":
            TribeMember.objects.filter(tribe=tribe, user=request.user).delete()

            request.user.message_set.create(message=ugettext("You have left the tribe %s") % tribe.name)
            if notification:
                pass # @@@
        are_member = has_member(tribe, request.user)
    else:
        tribe_form = form_class(instance=tribe)
    


    try:
        tm_visit = TribeMember.objects.get(tribe=tribe, user=request.user).last_visit
        topics = tribe.topics.filter(modified__gte=tm_visit)
        
        articles = Article.objects.filter(
            content_type=get_ct(tribe),
            object_id=tribe.id)
        total_articles = articles.count()
        articles = articles.filter(last_update__gte=tm_visit).order_by('-last_update')[:10]
        
        documents = Document.objects.filter(tribe=tribe, date_updated__gte=tm_visit).order_by('-date_updated')[:10]
    except: 
        topics          = None
        total_articles  = None
        articles        = None
        documents       = None
        topics          = None
        articles        = None
        total_articles  = None
        documents       = None
        
    return render_to_response(template_name, {
        "tribe_form"    : tribe_form,
        "tribe"         : tribe,
        "photos"        : photos,
        "topics"        : topics,
        "articles"      : articles,
        "documents"     : documents,
        "total_articles": total_articles,
        "are_member"    : are_member,
        "are_moderator" : is_moderator(tribe, request.user),
        "tribe_members_count" : TribeMember.objects.filter(tribe=tribe).count(),
    }, context_instance=RequestContext(request))

def tribe_members(request, slug, tribe_form=AddMemberForm, template_name="tribes/tribe_members.html"):
    
    tribe = get_object_or_404(Tribe, slug=slug)

    if tribe.deleted:
        raise Http404
    
    are_member = has_member(tribe, request.user)
    are_moderator = is_moderator(tribe, request.user)
    
    users = None
    tribe_members = None
    search_terms= ""
    search_terms_all = ""
    
    tribe_members_all = TribeMember.objects.filter(tribe=tribe).order_by('user__profile__name')
    
    order = request.GET.get('order')
    if order == 'date':
        tribe_members_all = tribe_members_all.order_by('-date_joined')
    else:
        tribe_members_all = tribe_members_all.order_by('user__profile__name')
        

    if tribe.private and not are_member:
        access = do_403_if_not_superuser(request)
        if access: 
            return access
    
    if are_moderator:

        if request.method == "GET":
            
            if 'search_members' in request.GET: 
                tribe_members = tribe_members_all
                search_terms = request.GET.get('search_members', '')
#                order = request.GET.get('order')
            
            elif 'search_all' in request.GET: 
                users = User.objects.all()
                search_terms_all = request.GET.get('search_all', '')
#                order = request.GET.get('order')

            if 'kick' in request.GET:
                try:
                    kicked_user_slug = request.GET['kick'] # lav til en form             
                    tm = TribeMember.objects.get(tribe=tribe, user__username=kicked_user_slug)
                    if not tm.user.id == tribe.creator.id:       
                        tm.delete()
                    else:
                        request.user.message_set.create(message=ugettext("You are the creator of this tribe so can't leave (yet)."))
                except:
                    pass
            
            elif 'invite' in request.GET:
                try:
                    invited_user_slug = request.GET['invite'] # lav til en form
                    
                    user = User.objects.get(username=invited_user_slug)
                    
                    tm = TribeMember(tribe=tribe, user=user)
                    if 'moderator' in request.GET:
                        tm.moderator=True
                    tm.save()
                except:
                    request.user.message_set.create(message=ugettext("%s is already a member of this tribe") % invited_user_slug)

            elif 'promote' in request.GET:
                try:
                    promoted_user_slug = request.GET['promote'] # lav til en form
                    user = User.objects.get(username=promoted_user_slug)
                    tm = TribeMember.objects.get(tribe=tribe, user=user)
                    tm.moderator=True
                    tm.save()
                except:
                    pass

            elif 'demote' in request.GET:
                try:
                    promoted_user_slug = request.GET['demote'] # lav til en form
                    
                    user = User.objects.get(username=promoted_user_slug)
                    
                    tm = TribeMember.objects.get(tribe=tribe, user=user)
                    tm.moderator=False
                    tm.save()
                except:
                    pass

            if search_terms:
                tribe_members = tribe_members.filter(user__profile__name__icontains=search_terms) | tribe_members.filter(user__username__icontains=search_terms) | tribe_members.filter(user__profile__nickname__icontains=search_terms)
            
            if search_terms_all:
                users = users.filter(profile__name__icontains=search_terms_all) | users.filter(username__icontains=search_terms_all) | users.filter(profile__nickname__icontains=search_terms_all)
    
    return render_to_response(template_name, {
            'tribe_members':tribe_members,
            'tribe_members_all':tribe_members_all,
            'users' : users,
            'order' : order,
            'search_terms_all' : search_terms_all ,
            'search_terms' : search_terms,
            "tribe_form": tribe_form,
            "tribe": tribe,
            "are_member": are_member,
            "are_moderator" : are_moderator,
        }, context_instance=RequestContext(request))

def topics(request, slug, form_class=TopicForm,
        template_name="tribes/topics.html"):
    tribe = get_object_or_404(Tribe, slug=slug)
    
    if tribe.deleted:
        raise Http404
    
    are_member = has_member(tribe, request.user),
    are_moderator =  is_moderator(tribe, request.user)
    
    if tribe.private and not are_member:
        access = do_403_if_not_superuser(request)
        if access: 
            return access
        
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
                    request.user.message_set.create(message=ugettext("You have started the topic %s") % topic.title)
                    if notification:
                        notification.send(tribe.member_users.all(), "tribes_new_topic", {"topic": topic})
                    topic_form = form_class() # @@@ is this the right way to reset it?
                    return HttpResponseRedirect(topic.get_absolute_url())
            else:
                request.user.message_set.create(message=ugettext("You are not a member and so cannot start a new topic"))
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
        "are_moderator" : are_moderator,
    }, context_instance=RequestContext(request))

def topic(request, id, edit=False, template_name="tribes/topic.html"):
    topic = get_object_or_404(Topic, id=id)
    
    if topic.tribe.deleted:
        raise Http404
    
    are_member = has_member(topic.tribe, request.user)
    
    if topic.tribe.private and not are_member:
        access = do_403_if_not_superuser(request)
        if access: 
            return access
                     
    if request.method == "POST" and edit == True:
        
        if is_moderator(topic.tribe, request.user):
                text = request.POST["body"]
                text += ugettext("<small><i>Topic editet by %(user)s : %(date)s</i></small>") % {'user' : request.user, 'date' : datetime.now()}
                topic.body = sanitize_html(text)
                topic.editet = datetime.now()
                topic.save()

        elif request.user == topic.creator:
            created = topic.created
            now = datetime.now()
            time_since = now - created
            if time_since.seconds < 60*20:
                topic.body = sanitize_html(request.POST["body"])
                topic.editet = datetime.now()
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
        "move_form" : MoveTribeForm(),
    }, context_instance=RequestContext(request))

@login_required
def topic_delete(request, pk):
    topic = Topic.objects.get(pk=pk)
    
    if topic.tribe.deleted:
        raise Http404
    
    are_member = has_member(topic.tribe, request.user)
    
    if topic.tribe.private and not are_member:
        access = do_403_if_not_superuser(request)
        if access: 
            return access
       
    if request.method == "POST" and (topic.creator == request.user or admin_group_access): 
        if forums:
            ThreadedComment.objects.all_for_object(topic).delete()
        send_to = topic.creator
        topic.delete()
        
        msg = Message(
            sender = request.user,
            recipient = send_to,
            subject = ugettext("A topic has been deleted."),
            body = ugettext("Your topic '%(topic)s' in '%(tribe)s' has been deleted by %(user)s") % {'topic' : topic.title,
                                                                             'user'  : request.user,
                                                                             'tribe' : topic.tribe },
        )
        msg.save()
    return HttpResponseRedirect(request.POST["next"])

@login_required
def topic_moderate(request, pk):
    topic = Topic.objects.get(pk=pk)
    
    if topic.tribe.deleted:
        raise Http404
    are_member = has_member(topic.tribe, request.user)
    
    if topic.tribe.private and not are_member:
        access = do_403_if_not_superuser(request)
        if access: 
            return access
    
    if request.method == "POST" and is_moderator(topic.tribe, request.user):
        print request.POST
        if 'sticky' in request.POST:
            topic.sticky = not topic.sticky
            topic.save()
        elif 'close' in request.POST:
            topic.closed = not topic.closed
            topic.save()
        elif 'move' in request.POST:
            topic_form = MoveTribeForm(request.POST)
            if topic_form.is_valid():
                try:
                    move_to = Tribe.objects.get(id=request.POST["tribes"])
                    from_tribe = topic.tribe
                    topic.tribe = move_to
                    topic.save()
                    request.user.message_set.create(message=ugettext("You have moved the topic to the group: %s") % move_to)
                    
                    dd = {'topic' : topic.title, 'user'  : request.user, 'tribe' : from_tribe,
                          'to' : move_to }

                    msg = Message(
                        sender = request.user,
                        recipient = topic.creator,
                        subject = ugettext("A topic has been Moved."),
                        body = ugettext("Your topic '%(topic)s' in '%(tribe)s' has been moved to %(to)s by %(user)s") % dd,
                    )
                    msg.save()
                except Tribe.DoesNotExist:
                    pass
    return HttpResponseRedirect(request.POST["next"])
