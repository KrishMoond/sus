from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# DRF Router
router = DefaultRouter()
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'follows', views.FollowViewSet)
router.register(r'hashtags', views.HashTagViewSet)

app_name = 'community'

urlpatterns = [
    # Traditional Django views
    path('', views.community_dashboard, name='dashboard'),
    path('discover/', views.discover_posts, name='discover'),
    path('post/<int:post_id>/react/', views.toggle_post_reaction, name='toggle_post_reaction'),
    path('post/<int:post_id>/join/', views.join_challenge, name='join_challenge'),
    path('challenges/', views.challenges_list, name='challenges'),
    path('challenges/create/', views.create_challenge, name='create_challenge'),
    path('user/<int:user_id>/follow/', views.toggle_follow, name='toggle_follow'),
    
    # API endpoints
    path('api/', include(router.urls)),
]