from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'following')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'

class Bookmark(models.Model):
    CONTENT_TYPES = [
        ('topic', 'Forum Topic'),
        ('project', 'Project'),
        ('event', 'Event'),
        ('resource', 'Resource'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username} bookmarked {self.content_type} #{self.object_id}'

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('topic_created', 'Created Topic'),
        ('post_created', 'Created Post'),
        ('project_created', 'Created Project'),
        ('project_joined', 'Joined Project'),
        ('event_created', 'Created Event'),
        ('resource_shared', 'Shared Resource'),
        ('user_followed', 'Followed User'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    content_type = models.CharField(max_length=20, blank=True)
    object_id = models.IntegerField(null=True, blank=True)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Activities'
    
    def __str__(self):
        return f'{self.user.username} - {self.get_activity_type_display()}'
