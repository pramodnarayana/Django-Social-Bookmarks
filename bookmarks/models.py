from django.db import models
from django.contrib.auth.models import User
from django_bookmarks.settings import SITE_HOST, DEFAULT_FROM_EMAIL
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
# Create your models here.
class Link(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url

    class Admin:
        pass


class Bookmark(models.Model):
    title = models.CharField(max_length = 200)
    user = models.ForeignKey(User)
    link = models.ForeignKey(Link)

    def __str__(self):
        return '{}, {}, {}'.format(self.user.username, self.link.url, self.title) 

    def get_absolute_url(self):
        return self.link.url

    class Admin:
        list_display = ('title', 'link', 'user')


class Tag(models.Model):
    name = models.CharField(max_length = 64, unique = True)
    bookmarks = models.ManyToManyField(Bookmark)

    def __str__(self):
        return self.name

    class Admin:
        pass


class SharedBookmark(models.Model):
    bookmark = models.ForeignKey(Bookmark, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=1)
    users_voted = models.ManyToManyField(User)
    def __str__(self):
        return '{}, {}'.format(self.bookmark, self.votes)

    class Admin:
        pass

class Friendship(models.Model):
    from_friend = models.ForeignKey(User, related_name='friend_set')
    to_friend = models.ForeignKey(User, related_name='to_friend_set')
    
    def __str__(self):
        return '{}, {}'.format(self.from_friend.username, self.to_friend.username)
    
    class Admin:
        pass
    class Meta:
        unique_together = (('to_friend', 'from_friend'), )
        
        
class Invitation(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    code = models.CharField(max_length=50)
    sender = models.ForeignKey(User)
    
    def __str__(self):
        return '{}, {}'.format(self.sender.username, self.email)
    
    def send_invitation(self):
        subject = 'Invitation to join Django Social Bookmarks'
        link = 'http://%s/friend/accept/%s' % (SITE_HOST, self.code)
        template = get_template('invitation_email.txt')
        context  = Context({
            'name': self.name,
            'link': link,
            'sender': self.sender.username                            
        })
        message = template.render(context)
        send_mail(subject, message, DEFAULT_FROM_EMAIL, [self.email])
        
    class Admin:
        pass
    
            