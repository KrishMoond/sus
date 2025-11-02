from django.urls import path
from .views import (
    ConversationListView, ConversationDetailView,
    MessageCreateView, start_conversation, FindUsersView
)

app_name = 'messaging'

urlpatterns = [
    path('', ConversationListView.as_view(), name='conversations'),
    path('find/', FindUsersView.as_view(), name='find_users'),
    path('<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('<int:conversation_pk>/messages/create/', MessageCreateView.as_view(), name='message_create'),
    path('start/<int:user_id>/', start_conversation, name='start_conversation'),
]

