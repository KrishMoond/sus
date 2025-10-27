from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
path('admin/', admin.site.urls),
path('accounts/', include('accounts.urls')),
path('profiles/', include('profiles.urls')),
path('forums/', include('forums.urls')),
path('resources/', include('resources.urls')),
path('events/', include('events.urls')),
path('projects/', include('projects.urls')),
path('messages/', include('messaging.urls')),
path('notifications/', include('notifications.urls')),
path('moderation/', include('moderation.urls')),
path('', include('forums.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)