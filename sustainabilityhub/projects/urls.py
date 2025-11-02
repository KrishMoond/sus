from django.urls import path
from .views import (
    ProjectListView, ProjectDetailView, ProjectCreateView,
    ProjectUpdateView, ProjectDeleteView, request_to_join,
    ProjectUpdateCreateView, ManageJoinRequestsView,
    approve_request, reject_request, ProjectChatView, send_chat_message
)

app_name = 'projects'

urlpatterns = [
    path('', ProjectListView.as_view(), name='list'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='detail'),
    path('create/', ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', ProjectDeleteView.as_view(), name='delete'),
    path('<int:pk>/request-join/', request_to_join, name='request_join'),
    path('<int:pk>/manage-requests/', ManageJoinRequestsView.as_view(), name='manage_requests'),
    path('requests/<int:pk>/approve/', approve_request, name='approve_request'),
    path('requests/<int:pk>/reject/', reject_request, name='reject_request'),
    path('<int:pk>/updates/create/', ProjectUpdateCreateView.as_view(), name='update_create'),
    path('<int:pk>/chat/', ProjectChatView.as_view(), name='chat'),
    path('<int:pk>/chat/send/', send_chat_message, name='chat_send'),
]

