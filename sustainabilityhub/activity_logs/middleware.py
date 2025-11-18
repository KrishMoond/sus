from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import ActivityLog, UserSession, SecurityEvent


class ActivityLogMiddleware(MiddlewareMixin):
    """Middleware to automatically log user activities"""
    
    def process_request(self, request):
        # Store request in thread-local storage for access in signals
        if hasattr(request, 'user') and request.user.is_authenticated:
            request._activity_log_data = {
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login activity"""
    ActivityLog.log_activity(
        user=user,
        action_type='user_login',
        description=f'User {user.username} logged in',
        request=request
    )
    
    # Create or update user session
    session_key = request.session.session_key
    if session_key:
        UserSession.objects.update_or_create(
            session_key=session_key,
            defaults={
                'user': user,
                'ip_address': ActivityLog.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'is_active': True,
            }
        )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout activity"""
    if user:
        ActivityLog.log_activity(
            user=user,
            action_type='user_logout',
            description=f'User {user.username} logged out',
            request=request
        )
        
        # Update user session
        session_key = request.session.session_key
        if session_key:
            try:
                session = UserSession.objects.get(session_key=session_key)
                session.is_active = False
                session.save()
            except UserSession.DoesNotExist:
                pass