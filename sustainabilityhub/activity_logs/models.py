from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ActivityLog(models.Model):
    """Track user activities across the platform"""
    ACTION_TYPES = [
        # User actions
        ('user_registered', 'User Registered'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('profile_updated', 'Profile Updated'),
        
        # Project actions
        ('project_created', 'Project Created'),
        ('project_joined', 'Project Joined'),
        ('project_left', 'Project Left'),
        ('project_updated', 'Project Updated'),
        
        # Event actions
        ('event_created', 'Event Created'),
        ('event_joined', 'Event Joined'),
        ('event_left', 'Event Left'),
        
        # Forum actions
        ('topic_created', 'Topic Created'),
        ('post_created', 'Post Created'),
        ('comment_created', 'Comment Created'),
        
        # Community actions
        ('community_post_created', 'Community Post Created'),
        ('community_comment_created', 'Community Comment Created'),
        ('user_followed', 'User Followed'),
        ('user_unfollowed', 'User Unfollowed'),
        
        # Resource actions
        ('resource_created', 'Resource Created'),
        ('resource_shared', 'Resource Shared'),
        
        # Admin actions
        ('user_warned', 'User Warned'),
        ('user_banned', 'User Banned'),
        ('content_moderated', 'Content Moderated'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='activity_logs'
    )
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    description = models.TextField(blank=True)
    
    # Generic relation to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.get_action_type_display()} - {self.created_at}'
    
    @classmethod
    def log_activity(cls, user, action_type, description='', content_object=None, metadata=None, request=None):
        """Helper method to log activities"""
        log_data = {
            'user': user,
            'action_type': action_type,
            'description': description,
            'metadata': metadata or {},
        }
        
        if content_object:
            log_data['content_object'] = content_object
        
        if request:
            log_data['ip_address'] = cls.get_client_ip(request)
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return cls.objects.create(**log_data)
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserSession(models.Model):
    """Track user sessions"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions_log'
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=200, blank=True)  # City, Country
    device_type = models.CharField(max_length=50, blank=True)  # Mobile, Desktop, Tablet
    browser = models.CharField(max_length=100, blank=True)
    
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
        indexes = [
            models.Index(fields=['user', '-login_time']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f'{self.user.username} - {self.login_time}'
    
    @property
    def duration(self):
        """Calculate session duration"""
        if self.logout_time:
            return self.logout_time - self.login_time
        return None


class SecurityEvent(models.Model):
    """Track security-related events"""
    EVENT_TYPES = [
        ('failed_login', 'Failed Login Attempt'),
        ('password_changed', 'Password Changed'),
        ('email_changed', 'Email Changed'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('two_factor_enabled', 'Two Factor Authentication Enabled'),
        ('two_factor_disabled', 'Two Factor Authentication Disabled'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='security_events',
        null=True,
        blank=True
    )
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['ip_address', '-created_at']),
        ]
    
    def __str__(self):
        username = self.user.username if self.user else 'Anonymous'
        return f'{username} - {self.get_event_type_display()} - {self.created_at}'