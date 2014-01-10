from django.contrib.syndication.views import Feed
from bookmarks.models import Bookmark
from django.contrib.auth.models import User 
from django.core.exceptions import ObjectDoesNotExist

class RecentBookmarks(Feed):
    title_template = 'feeds/title.html'
    description_template = 'feeds/description.html'

    title = 'Django Bookmarks | Recent Bookmarks'
    link = '/sitenews/'
    description = 'Recent Bookmarks posted to Django Bookmarks'
    
    def items(self):
        return Bookmark.objects.order_by('-id')[:10]

    def item_link(self, item):
        return item.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(RecentBookmarks, self).get_context_data(**kwargs)
        #print(context)
        return context


class UserBookmarks(Feed):
    title_template = 'feeds/user_title.html'
    description_template = 'feeds/user_description.html'

    def get_object(self, request, uname=None):
        if len(uname) == None:
            raise ObjectDoesNotExist
        return User.objects.get(username=uname)

    def title(self, user):
        return 'Django Bookmarks | Bookmarks for {}'.format(user.username)

    def link(self, user):
        return '/feeds/user/{}'.format(user.username)

    def description(self, user):
        return 'Recent bookmarks posted by {}'.format(user.username)

    def items(self, user):
        return user.bookmark_set.order_by('-id')[:10]
