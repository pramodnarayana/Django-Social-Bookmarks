from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.context_processors import csrf
from django.template import Context
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from bookmarks.forms import RegistrationForm, BookmarkSaveForm, SearchForm, FriendInviteForm
from bookmarks.models import Link, Bookmark, Tag, SharedBookmark, Friendship, Invitation
import json
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext as _

ITEMS_PER_PAGE = 2
# Create your views here.

def main_page(request):
    shared_bookmarks = SharedBookmark.objects.order_by('-date')[:10]
    variables = RequestContext(request, {
        'shared_bookmarks' : shared_bookmarks
    })
    return render_to_response('main_page.html', variables) 


def user_page(request, username):
    print(username)
    try:
        #user = User.objects.get(username=username)
        user = get_object_or_404(User, username=username)
        query_set = user.bookmark_set.order_by('-id')
        is_friend = Friendship.objects.filter(from_friend=request.user, to_friend=user)
        paginator, bookmarks, page = __bookmark_paginator(request, query_set)
    except:
        raise Http404('Requested user not found')
    #bookmarks = user.bookmark_set.all()
    is_friend = Friendship.objects.filter(from_friend=request.user, to_friend=user)
    return render_to_response(
        'user_page.html',
        RequestContext(request, {
        'username' : username,
        'bookmarks' : bookmarks,
        'show_tags' : True,
        'show_edit' : username == request.user.username,
        'show_delete' : username == request.user.username,
        'show_paginator': paginator.num_pages > 1,
        'has_prev': bookmarks.has_previous(),
        'has_next': bookmarks.has_next(),
        'page': page,
        'pages': paginator.num_pages,
        'next_page': page + 1,
        'prev_page': page - 1,
        'is_friend': is_friend
        })
    )

def __bookmark_paginator(request, query_set):
    paginator = Paginator(query_set, ITEMS_PER_PAGE)
    try:
        page = int(request.GET['page'])
    except:
        page = 1
    try:
        bookmarks = paginator.page(page)
    except:
        raise Http404('Page not found')
    #print('bookmarks =', bookmarks, 'page = ', page)
    return (paginator, bookmarks, page)    
    
def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/login')


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )
            if 'invitation' in request.session:
                #Retrieve the invitation object
                invitation = Invitation.objects.get(id=request.session['invitation'])
                #Create friendship from user to sender
                friendship = Friendship(from_friend=user, to_friend=invitation.sender)
                friendship.save()
                #Create friendship from sender to user
                friendship = Friendship(from_friend=invitation.sender, to_friend=user)
                friendship.save()
                #Delete the invitation from the database
                invitation.delete()
                del request.session['invitation']
            return HttpResponseRedirect('/register/success/') 
    else:
        form = RegistrationForm()
        print(form.as_p())
    variables = RequestContext(request, {'form' : form})
    return render_to_response('registration/register.html', variables)

@login_required
def bookmark_delete(request):
    if request.method == 'POST':
        if 'url' in request.POST:
            url = request.POST['url']
            try:
                link = Link.objects.get(url=url)
                Bookmark.objects.get(user=request.user, link=link).delete()
            except ObjectDoesNotExist:
                return HttpResponseRedirect('/user/{}/'.format(request.user.username))
            return HttpResponse('Success')
    return HttpResponseRedirect('/user/{}/'.format(request.user.username))

@login_required
def bookmark_save_page(request):
    ajax = False
    if 'ajax' in request.GET.keys():
        ajax = True

    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        if form.is_valid():
            bookmark = _bookmark_save_page(request, form)
            if ajax:
                print('bookmark = ', bookmark)
                variables = RequestContext(request, {
                    'bookmarks' : [bookmark],
                    'show_edit': True,
                    'show_tags': True
                })
                data =  render_to_response('bookmark_list.html', variables)
                print(data)
                return data 
            else:
                return HttpResponseRedirect('/user/{}/'.format(request.user.username))
        else:
            if ajax:
                return HttpResponse('failure')
    elif 'url' in request.GET:
        url = request.GET['url']
        title = ''
        tags = ''
        try:
            link = Link.objects.get(url=url)
            bookmark = Bookmark.objects.get(link=link, user=request.user)
            title = bookmark.title
            tags = ' '.join(tag.name for tag in bookmark.tag_set.all())
        except ObjectDoesNotExist:
            pass
        form = BookmarkSaveForm({
            'url' : url,
            'title' : title,
            'tags' : tags
        })
        
    else:
        form = BookmarkSaveForm()
    variables = RequestContext(request, {'form' : form})
    if ajax:
        return render_to_response('bookmark_save_form.html', variables)
    else:
        print('Loading Page')
        return render_to_response('bookmark_save.html', variables)


def _bookmark_save_page(request, form):
    # Create or get link.
    link, dummy = Link.objects.get_or_create(url=form.cleaned_data['url'])
    # Create or get bookmark.
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, link=link)
    # Update bookmark title.
    bookmark.title = form.cleaned_data['title']
    # If the bookmark is being updated, clear old tag list.
    if not created:
        bookmark.tag_set.clear()
    # Create new tag list.
    tag_names = form.cleaned_data['tags'].split()
    for tag_name in tag_names:
        tag, dummy = Tag.objects.get_or_create(name=tag_name)
        bookmark.tag_set.add(tag)
  
    #Share on the main page if requested
    print(form.cleaned_data)
    if form.cleaned_data['share']:
        shared_bookmark, created = SharedBookmark.objects.get_or_create(bookmark=bookmark)
        print('shared_bookmark = {}\t created = {}'.format(shared_bookmark, created))
        if created:
            shared_bookmark.users_voted.add(request.user)
            shared_bookmark.save()
        
    # Save bookmark to database.
    bookmark.save()
    return bookmark
    
        
def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    bookmarks = tag.bookmarks.order_by('-id')
    variables = RequestContext(request, {
        'bookmarks' : bookmarks,
        'tag_name' : tag_name,
        'show_tags' : True,
        'show_user' : True
    })
    return render_to_response('tag_page.html', variables)


def tag_cloud_page(request):
    MAX_WEIGHT = 5
    min_count = max_count = 0 
    tags = Tag.objects.order_by('name')
    # Calculate tag, min and max counts.
    if tags:
        min_count = max_count = tags[0].bookmarks.count()
    for tag in tags:
        tag.count = tag.bookmarks.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count
    # Calculate count range. Avoid dividing by zero.
    tag_range = float(max_count - min_count)
    if tag_range == 0.0:
        tag_range = 1.0
    # Calculate tag weights.
    for tag in tags:
        tag.weight = int(MAX_WEIGHT * (tag.count - min_count) / tag_range)
        print('tag_name = {}\t tag_weight = {}'.format(tag.name, tag.weight))
    variables = RequestContext(request, {
        'tags': tags
    })
    return render_to_response('tag_cloud_page.html', variables)



def search_page(request):
    form = SearchForm()
    bookmarks = []
    show_results = False
    if 'query' in request.GET:
    #if request.GET.has_key('query'):
        show_results = True
        query = request.GET['query'].strip()
        if query:
            keywords = query.split()
            q = Q()
            for keyword in keywords:
                q = q & Q(title__icontains=keyword)
            print(q)
            form = SearchForm({'query' : query})
            bookmarks = Bookmark.objects.filter(q)[:10]
    variables = RequestContext(request, {
        'form' : form,
        'bookmarks' : bookmarks,
        'show_results' : show_results,
        'show_tags' : True,
        'show_user' : True,
    })
    if 'ajax' in request.GET:
        #print('variables = ', variables)
        #Returns the result for the search
        return render_to_response('bookmark_list.html', variables)
    else:
        #Returns simple search form
        return render_to_response('search.html', variables)


def ajax_tag_autocomplete(request):
    print(request)
    if 'term' in request.POST.keys():
        tags =  Tag.objects.filter(name__icontains=request.POST['term'])[:10]
        data = [tag.name for tag in tags]
        return HttpResponse(json.dumps(data), 'application/json') #input to json should be python list object 
    return HttpResponse()


@login_required
def bookmark_vote_page(request):
    if 'id' in request.GET:
        try:
            bookmark_id = request.GET['id']
            shared_bookmark = SharedBookmark.objects.get(id=bookmark_id)
            user_voted = shared_bookmark.users_voted.filter(username=request.user.username)
            if not user_voted :
                shared_bookmark.votes += 1
                shared_bookmark.users_voted.add(request.user)
                shared_bookmark.save()
        except ObjectDoesNotExist:
            raise Http404('Bookmark not found')
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect('/')



def popular_page(request):
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    shared_bookmarks = SharedBookmark.objects.filter(date__gt=yesterday)
    popular_bookmarks = shared_bookmarks.order_by('-votes')[:10]
    variables = RequestContext(request, {
        'shared_bookmarks': popular_bookmarks
    })
    return render_to_response('popular_page.html', variables)

def bookmark_page(request, bookmark_id):
    shared_bookmark = get_object_or_404(SharedBookmark, id=bookmark_id)
    #ctype = ContentType.objects.get(app_label='bookmarks', model='sharedbookmark')
    variables = RequestContext(request, {
        'shared_bookmark': shared_bookmark,
    })
    print('variables = ', variables)
    #variables.update(csrf(request))
    return render_to_response('bookmark_page.html', variables) 

def friends_page(request, username):
    user = get_object_or_404(User, username=username)
    friends = [friendship.to_friend for friendship in user.friend_set.all()]
    query_set = Bookmark.objects.filter(user__in=friends).order_by('-id')
    paginator, friends_bookmarks, page = __bookmark_paginator(request, query_set)
    print('friends_bookmarks = ', friends_bookmarks, 'page = ', page)
    variables = RequestContext(request, {
        'username': username,
        'friends': friends,
        'bookmarks': friends_bookmarks,
        'show_tags': True,
        'show_user': True,
        'show_paginator': paginator.num_pages > 1,
        'has_prev': friends_bookmarks.has_previous(),
        'has_next': friends_bookmarks.has_next(),
        'page': page,
        'pages': paginator.num_pages,
        'next_page': page + 1,
        'prev_page': page - 1,                                         
    })
    return render_to_response('friends_page.html', variables)

@login_required
def friend_add(request):
    if 'username' in request.GET.keys():
        friend = get_object_or_404(User, username=request.GET['username'])
        friendship = Friendship(from_friend=request.user, to_friend=friend)
        friendship.save()
        return HttpResponseRedirect('/friends/{}/'.format(request.user.username))
    else:
        raise Http404('user not found')

def my_image(request):
    image_data = open("site_media/images/yify.jpg", "rb").read()
    return HttpResponse(image_data, mimetype="image/png")


@login_required
def friend_invite(request):
    if request.method == 'POST':
        form = FriendInviteForm(request.POST)
        if form.is_valid():
            invitation = Invitation(
                name = form.cleaned_data['name'],
                email = form.cleaned_data['email'],
                code = User.objects.make_random_password(20),
                sender = request.user
            )
            invitation.save()
            try:
                invitation.send_invitation()
                request.user.message_set.create(message=_('An invitation was sent to %s.') % invitation.email)
            except:
                request.user.message_set.create(message=_('There was an error while sending the invitation.'))
                
            return HttpResponseRedirect('/friend/invite')
    else:
        form = FriendInviteForm()
    variables = RequestContext(request, {
        'form':form
    })
    return render_to_response('friend_invite.html', variables)
            

def friend_accept(request, code):
    invitation = get_object_or_404(Invitation, code__exact=code)
    request.session['invitation'] = invitation.id
    return HttpResponseRedirect('/register')
           
