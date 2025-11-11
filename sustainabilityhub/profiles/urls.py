from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('<str:username>/', views.profile_detail, name='detail'),
    path('edit/', views.profile_edit, name='edit'),
    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('bookmark/toggle/', views.toggle_bookmark, name='toggle_bookmark'),
    path('bookmarks/', views.my_bookmarks, name='bookmarks'),
    path('feed/', views.activity_feed, name='feed'),
]
