from django.urls import path
from .views import (
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    TopicListView, TopicDetailView,
    TopicCreateView, TopicUpdateView, TopicDeleteView,
    LegacyPostCreateView, LegacyPostUpdateView, LegacyPostDeleteView,
    like_topic, create_post, toggle_reaction, add_comment, edit_post, delete_post
)

app_name = 'forums'

urlpatterns = [
    # Social Media Feed
    path('', TopicListView.as_view(), name='topics'),
    path('create-post/', create_post, name='create_post'),
    path('posts/<int:post_id>/react/', toggle_reaction, name='toggle_reaction'),
    path('posts/<int:post_id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:post_id>/edit/', edit_post, name='edit_post'),
    path('posts/<int:post_id>/delete/', delete_post, name='delete_post'),
    
    # Legacy Forum URLs
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('topics/create/', TopicCreateView.as_view(), name='topic_create'),
    path('topics/<int:pk>/edit/', TopicUpdateView.as_view(), name='topic_update'),
    path('topics/<int:pk>/delete/', TopicDeleteView.as_view(), name='topic_delete'),
    path('topics/<int:pk>/like/', like_topic, name='topic_like'),
    path('topics/<int:topic_pk>/posts/create/', LegacyPostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', LegacyPostUpdateView.as_view(), name='legacy_post_update'),
    path('posts/<int:pk>/delete/', LegacyPostDeleteView.as_view(), name='legacy_post_delete'),
]

