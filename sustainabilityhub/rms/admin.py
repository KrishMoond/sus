from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['subject', 'category', 'reporter', 'status', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['subject', 'description', 'reporter__username']
    readonly_fields = ['created_at']