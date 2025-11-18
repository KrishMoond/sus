from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import views as auth_views
from forums.views import home_view
from accounts import views
from sustainabilityhub.search_views import global_search

# Customize admin site
admin.site.site_header = "Sustainability Hub Administration"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Sustainability Hub Admin"

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('', home_view, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('forums/', include('forums.urls')),
    path('resources/', include('resources.urls')),
    path('events/', include('events.urls')),
    path('projects/', include('projects.urls')),
    path('messages/', include('messaging.urls')),
    path('notifications/', include('notifications.urls')),
    path('moderation/', include('moderation.urls')),
    path('reports/', include('rms.urls')),
    path('community/', include('community.urls')),
    path('search/', global_search, name='global_search'),
    
    # API endpoints
    path('api/auth/', include('accounts.api_urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)