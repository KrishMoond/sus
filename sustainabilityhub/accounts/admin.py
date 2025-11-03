from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserWarning
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    
    list_display = ['username', 'email', 'full_name', 'is_active', 'is_staff', 'date_joined', 'user_status', 'avatar_preview']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    actions = ['deactivate_users', 'activate_users', 'make_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('bio', 'avatar')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {'fields': ('email',)}),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}" if obj.first_name or obj.last_name else "No name set"
    full_name.short_description = 'Full Name'
    
    def user_status(self, obj):
        if obj.is_superuser:
            return format_html('<span style="color: gold; font-weight: bold;">🛡️ Superuser</span>')
        elif not obj.is_active:
            return format_html('<span style="color: red; font-weight: bold;">❌ Deactivated</span>')
        elif obj.is_staff:
            return format_html('<span style="color: blue; font-weight: bold;">🛠️ Staff</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">✅ Active</span>')
    user_status.short_description = 'Status'
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />', obj.avatar.url)
        return format_html('<div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #2d8659, #238b4e); display: inline-flex; align-items: center; justify-content: center; color: white; font-weight: bold;">{}</div>', obj.username[0].upper() if obj.username else '?')
    avatar_preview.short_description = 'Avatar'
    
    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} users deactivated for policy violations.')
    deactivate_users.short_description = "Deactivate selected users (Policy Violation)"
    
    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} users reactivated.')
    activate_users.short_description = "Reactivate selected users"
    
    def make_staff(self, request, queryset):
        count = queryset.update(is_staff=True)
        self.message_user(request, f'{count} users granted staff privileges.')
    make_staff.short_description = "Grant staff privileges"


@admin.register(UserWarning)
class UserWarningAdmin(admin.ModelAdmin):
    list_display = ['user', 'severity', 'reason', 'issued_by', 'created_at']
    list_filter = ['severity', 'created_at', 'is_active']
    search_fields = ['user__username', 'reason', 'description']
    readonly_fields = ['created_at']