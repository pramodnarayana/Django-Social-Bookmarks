from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from django_bookmarks.settings import BASE_DIR
import os
from django.views.generic import TemplateView
from bookmarks.feeds import RecentBookmarks
from bookmarks.feeds import UserBookmarks

site_media = os.path.join(BASE_DIR, 'site_media')

feeds = {
    'recent' : RecentBookmarks,
    'user': UserBookmarks
}

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    #Admin interface
    url(r'^admin/', include(admin.site.urls)),
    #Ajax 
    url(r'^ajax/tag/autocomplete', 'bookmarks.views.ajax_tag_autocomplete'),
    #Browsing 
    url(r'^$', 'bookmarks.views.main_page'),
    url(r'^user/(\w+)/$', 'bookmarks.views.user_page'),
    url(r'^tag/([^\s]+)/$', 'bookmarks.views.tag_page'),
    url(r'^tag/$', 'bookmarks.views.tag_cloud_page'),
    url(r'^search/$', 'bookmarks.views.search_page'),
    url(r'^vote/$', 'bookmarks.views.bookmark_vote_page'),
    url(r'^popular/$', 'bookmarks.views.popular_page'),
    url(r'^bookmark/(\d+)/$', 'bookmarks.views.bookmark_page'),
    #Comments
    url(r'comments/', include('django.contrib.comments.urls')),
    #Feeds
    #url(r'feeds/(?P<url>.*)/$', 'django.contrib.syndication.views', {'feed_dict': feeds}),
    url(r'feeds/recent/$', RecentBookmarks()),
    url(r'feeds/user/(?P<uname>\w+)/$', UserBookmarks()),
    #url(r'feeds/user/(?P<bits>\w+)$', UserBookmarks()),
    #Friends
    url(r'^friends/(\w+)/$', 'bookmarks.views.friends_page'),
    url(r'^friend/add/$', 'bookmarks.views.friend_add'),
    url(r'^friend/invite/$', 'bookmarks.views.friend_invite'),
    url(r'^friend/accept/(\w+)/$', 'bookmarks.views.friend_accept'),
    # Session management
    url(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^logout/$', 'bookmarks.views.logout_page'),
    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root' : site_media}),
    url(r'^register/$', 'bookmarks.views.register_page'),
    url(r'^register/success/$', TemplateView.as_view(template_name='registration/register_success.html')),
    # Account management
    url(r'^save/$', 'bookmarks.views.bookmark_save_page'),
    url(r'^image/$', 'bookmarks.views.my_image')
)
