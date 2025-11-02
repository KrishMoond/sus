from django.urls import path
from .views import (
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    TopicListView, TopicDetailView,
    TopicCreateView, TopicUpdateView, TopicDeleteView,
    PostCreateView, PostUpdateView, PostDeleteView,
    like_topic
)

app_name = 'forums'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('topics/', TopicListView.as_view(), name='topics'),
    path('topics/<int:pk>/', TopicDetailView.as_view(), name='topic_detail'),
    path('topics/create/', TopicCreateView.as_view(), name='topic_create'),
    path('topics/<int:pk>/edit/', TopicUpdateView.as_view(), name='topic_update'),
    path('topics/<int:pk>/delete/', TopicDeleteView.as_view(), name='topic_delete'),
    path('topics/<int:pk>/like/', like_topic, name='topic_like'),
    path('topics/<int:topic_pk>/posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
]

