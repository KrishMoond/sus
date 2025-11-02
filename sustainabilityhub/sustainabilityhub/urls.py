from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from forums.views import home_view

# Customize admin site
admin.site.site_header = "Sustainability Hub Administration"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Sustainability Hub Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),  # Home page without namespace conflict
    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('forums/', include('forums.urls')),
    path('resources/', include('resources.urls')),
    path('events/', include('events.urls')),
    path('projects/', include('projects.urls')),
    path('messages/', include('messaging.urls')),
    path('notifications/', include('notifications.urls')),
    path('moderation/', include('moderation.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)