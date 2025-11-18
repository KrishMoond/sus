from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# DRF Router
router = DefaultRouter()
router.register(r'users', api_views.UserViewSet)
router.register(r'warnings', api_views.UserWarningViewSet)

urlpatterns = [
    # Authentication endpoints
    path('register/', api_views.register_user, name='api_register'),
    path('login/', api_views.login_user, name='api_login'),
    path('logout/', api_views.logout_user, name='api_logout'),
    
    # Dashboard
    path('dashboard/stats/', api_views.user_dashboard_stats, name='api_dashboard_stats'),
    
    # Router URLs
    path('', include(router.urls)),
]