from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar = models.FileField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.username


class UserWarning(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low - Minor Violation'),
        ('medium', 'Medium - Policy Violation'),
        ('high', 'High - Serious Violation'),
        ('final', 'Final Warning'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warnings')
    issued_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='warnings_issued')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    reason = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_severity_display()} warning for {self.user.username}'