from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Max
from django.utils import timezone
from .models import Conversation, Message


class ConversationListView(LoginRequiredMixin, ListView):
    model = Conversation
    template_name = 'messaging/conversations.html'
    context_object_name = 'conversations'
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).annotate(
            last_message_time=Max('messages__created_at')
        ).order_by('-last_message_time').distinct()


class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = Conversation
    template_name = 'messaging/conversation_detail.html'
    context_object_name = 'conversation'
    
    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_list'] = self.object.messages.all().select_related('sender')
        # Mark messages as read
        self.object.messages.exclude(
            sender=self.request.user
        ).filter(is_read=False).update(is_read=True, read_at=timezone.now())
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    template_name = 'messaging/message_form.html'
    fields = ['content']
    
    def form_valid(self, form):
        conversation = get_object_or_404(
            Conversation,
            pk=self.kwargs['conversation_pk'],
            participants=self.request.user
        )
        form.instance.conversation = conversation
        form.instance.sender = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('messaging:conversation_detail', kwargs={'pk': self.kwargs['conversation_pk']})


def start_conversation(request, user_id):
    from django.contrib.auth import get_user_model
    
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to send messages.')
        return redirect('login')
    
    User = get_user_model()
    other_user = get_object_or_404(User, pk=user_id)
    
    if request.user == other_user:
        messages.error(request, 'You cannot message yourself.')
        return redirect('profiles:detail', username=other_user.username)
    
    # Find existing conversation or create new one
    conversations = Conversation.objects.filter(participants=request.user)
    conversation = conversations.filter(participants=other_user).distinct().first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
        messages.success(request, f'Started conversation with {other_user.username}.')
    
    return redirect('messaging:conversation_detail', pk=conversation.pk)


class FindUsersView(LoginRequiredMixin, ListView):
    """View to find and message any user in the community"""
    from django.contrib.auth import get_user_model
    
    template_name = 'messaging/find_users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        User = get_user_model()
        queryset = User.objects.exclude(id=self.request.user.id).select_related('profile')
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset.order_by('username')
