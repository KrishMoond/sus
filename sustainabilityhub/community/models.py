from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Post(models.Model):
    """Community feed posts"""
    POST_TYPES = [
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('link', 'Link Share'),
        ('achievement', 'Achievement'),
        ('challenge', 'Sustainability Challenge'),
        ('tip', 'Eco Tip'),
        ('milestone', 'Project Milestone'),
        ('impact', 'Environmental Impact'),
    ]
    
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    content = models.TextField()
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    image = models.ImageField(upload_to='community/posts/', null=True, blank=True)
    link_url = models.URLField(null=True, blank=True)
    link_title = models.CharField(max_length=200, null=True, blank=True)
    
    # Generic relation to link posts to projects, events, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Sustainability-specific fields
    carbon_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="CO2 saved in kg")
    location = models.CharField(max_length=200, blank=True, help_text="Location for local impact")
    challenge_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Challenge duration in days")
    participants_count = models.PositiveIntegerField(default=0)
    impact_category = models.CharField(max_length=50, choices=[
        ('energy', 'Energy Saving'),
        ('waste', 'Waste Reduction'),
        ('transport', 'Sustainable Transport'),
        ('food', 'Sustainable Food'),
        ('water', 'Water Conservation'),
        ('biodiversity', 'Biodiversity Protection'),
    ], blank=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.author.username} - {self.post_type} - {self.created_at.strftime("%Y-%m-%d")}'
    
    @property
    def total_reactions(self):
        return self.reactions.count()
    
    @property
    def total_comments(self):
        return self.comments.count()


class PostReaction(models.Model):
    """Reactions to community posts"""
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('celebrate', '🎉'),
        ('support', '🤝'),
        ('inspire', '✨'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_post_reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['post', 'user']
        indexes = [
            models.Index(fields=['post', 'reaction_type']),
        ]
    
    def __str__(self):
        return f'{self.user.username} {self.get_reaction_type_display()} post {self.post.id}'


class Comment(models.Model):
    """Comments on community posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author.username} on post {self.post.id}'
    
    @property
    def total_reactions(self):
        return self.reactions.count()


class CommentReaction(models.Model):
    """Reactions to comments"""
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
    ]
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_comment_reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES, default='like')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f'{self.user.username} {self.get_reaction_type_display()} comment {self.comment.id}'


class Follow(models.Model):
    """User following system"""
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_following')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]
    
    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


class HashTag(models.Model):
    """Hashtags for posts"""
    name = models.CharField(max_length=100, unique=True)
    posts = models.ManyToManyField(Post, related_name='hashtags', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f'#{self.name}'
    
    @property
    def post_count(self):
        return self.posts.count()


class ChallengeParticipation(models.Model):
    """Track user participation in challenges"""
    challenge_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='participants', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completion_proof = models.ImageField(upload_to='challenge_proofs/', null=True, blank=True)
    impact_achieved = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'challenge_post']
    
    def __str__(self):
        return f'{self.user.username} - Challenge Participation'


