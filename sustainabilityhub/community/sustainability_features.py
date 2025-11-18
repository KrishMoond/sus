"""
Unique sustainability features for community app
"""
from django.db import models
from django.conf import settings
from .models import Post


class ImpactTracker(models.Model):
    """Track environmental impact of user actions"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='impact_records')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    impact_type = models.CharField(max_length=50, choices=[
        ('carbon_saved', 'Carbon Footprint Reduced'),
        ('waste_reduced', 'Waste Reduced'),
        ('energy_saved', 'Energy Saved'),
        ('water_saved', 'Water Conserved'),
        ('trees_planted', 'Trees Planted'),
        ('plastic_avoided', 'Plastic Avoided'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='kg')
    date_recorded = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-date_recorded']


class EcoTip(models.Model):
    """Daily eco tips and sustainability advice"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('energy', 'Energy Saving'),
        ('waste', 'Waste Reduction'),
        ('transport', 'Green Transport'),
        ('food', 'Sustainable Eating'),
        ('home', 'Eco Home'),
        ('shopping', 'Conscious Shopping'),
    ])
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Advanced'),
    ])
    estimated_impact = models.CharField(max_length=100, help_text="e.g., 'Saves 2kg CO2 per month'")
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']


class LocalImpactGroup(models.Model):
    """Location-based sustainability groups"""
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='local_groups')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.location}"


class SustainabilityBadge(models.Model):
    """Achievement badges for sustainability actions"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='🏆')
    criteria = models.JSONField(help_text="Requirements to earn this badge")
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ], default='common')
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """User's earned badges"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(SustainabilityBadge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'badge']