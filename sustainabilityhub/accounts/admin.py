from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined', 'avatar_preview']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('bio', 'avatar')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {'fields': ('email',)}),
    )
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', obj.avatar.url)
        return format_html('<div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #2d8659, #238b4e); display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold;">{}</div>', obj.username[0].upper() if obj.username else '?')
    avatar_preview.short_description = 'Avatar'