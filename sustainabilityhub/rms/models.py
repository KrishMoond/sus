from django.db import models
from django.conf import settings

class Report(models.Model):
    CATEGORY_CHOICES = [
        ('spam', 'Spam/Unwanted Content'),
        ('harassment', 'Harassment/Bullying'),
        ('inappropriate', 'Inappropriate Content'),
        ('fake', 'Fake Information'),
        ('technical', 'Technical Issue'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('investigating', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rms_reports_made')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    admin_response = models.TextField(blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='rms_reports_resolved')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.get_category_display()} - {self.subject}'

class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Feedback from {self.user.username} - {self.rating}/5'