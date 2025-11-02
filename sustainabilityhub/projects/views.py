from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django import forms
from .models import Project, ProjectUpdate, ProjectJoinRequest, ProjectChat, ProjectChatMessage


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 12


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = context['project']
        
        # Check if user has pending request
        if self.request.user.is_authenticated:
            pending_request = ProjectJoinRequest.objects.filter(
                project=project,
                user=self.request.user,
                status='pending'
            ).first()
            context['pending_request'] = pending_request
            
            # Show pending requests for creator
            if self.request.user == project.creator:
                context['pending_requests'] = ProjectJoinRequest.objects.filter(
                    project=project,
                    status='pending'
                ).order_by('-created_at')
        
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/form.html'
    fields = ['title', 'description', 'status', 'start_date', 'end_date', 'tags', 'image']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/form.html'
    fields = ['title', 'description', 'status', 'start_date', 'end_date', 'tags', 'image']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form
    
    def get_queryset(self):
        return Project.objects.filter(creator=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/confirm_delete.html'
    success_url = reverse_lazy('projects:list')
    
    def get_queryset(self):
        return Project.objects.filter(creator=self.request.user)


def request_to_join(request, pk):
    """Create a join request instead of direct join"""
    project = get_object_or_404(Project, pk=pk)
    
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to request to join a project.')
        return redirect('login')
    
    if request.user == project.creator:
        messages.info(request, 'You are already the creator of this project.')
        return redirect('projects:detail', pk=pk)
    
    if request.user in project.members.all():
        messages.info(request, 'You are already a member of this project.')
        return redirect('projects:detail', pk=pk)
    
    # Check if there's already a pending request
    existing_request = ProjectJoinRequest.objects.filter(
        project=project,
        user=request.user,
        status='pending'
    ).first()
    
    if existing_request:
        messages.info(request, 'You already have a pending request for this project.')
        return redirect('projects:detail', pk=pk)
    
    # Create new request
    message = request.POST.get('message', '')
    join_request = ProjectJoinRequest.objects.create(
        project=project,
        user=request.user,
        message=message
    )
    
    messages.success(request, f'Join request sent to {project.creator.username}. You will be notified when they respond.')
    return redirect('projects:detail', pk=pk)


class ManageJoinRequestsView(LoginRequiredMixin, ListView):
    """View for project creator to manage join requests"""
    model = ProjectJoinRequest
    template_name = 'projects/manage_requests.html'
    context_object_name = 'requests'
    
    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        if project.creator != self.request.user:
            raise PermissionDenied("You are not the creator of this project.")
        
        return ProjectJoinRequest.objects.filter(
            project=project,
            status='pending'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs['pk'])
        return context


def approve_request(request, pk):
    """Approve a join request"""
    join_request = get_object_or_404(ProjectJoinRequest, pk=pk)
    
    if join_request.project.creator != request.user:
        messages.error(request, 'You do not have permission to approve this request.')
        return redirect('projects:detail', pk=join_request.project.pk)
    
    if join_request.status != 'pending':
        messages.error(request, 'This request has already been processed.')
        return redirect('projects:detail', pk=join_request.project.pk)
    
    # Approve the request
    join_request.status = 'approved'
    join_request.reviewed_at = timezone.now()
    join_request.reviewed_by = request.user
    join_request.save()
    
    # Add user to project members
    join_request.project.members.add(join_request.user)
    
    messages.success(request, f'You approved {join_request.user.username}\'s request to join.')
    return redirect('projects:manage_requests', pk=join_request.project.pk)


def reject_request(request, pk):
    """Reject a join request"""
    join_request = get_object_or_404(ProjectJoinRequest, pk=pk)
    
    if join_request.project.creator != request.user:
        messages.error(request, 'You do not have permission to reject this request.')
        return redirect('projects:detail', pk=join_request.project.pk)
    
    if join_request.status != 'pending':
        messages.error(request, 'This request has already been processed.')
        return redirect('projects:detail', pk=join_request.project.pk)
    
    # Reject the request
    join_request.status = 'rejected'
    join_request.reviewed_at = timezone.now()
    join_request.reviewed_by = request.user
    join_request.save()
    
    messages.info(request, f'You declined {join_request.user.username}\'s request.')
    return redirect('projects:manage_requests', pk=join_request.project.pk)


class ProjectChatView(LoginRequiredMixin, DetailView):
    """View for project chat room - only accessible to project members"""
    model = Project
    template_name = 'projects/chat.html'
    context_object_name = 'project'
    
    def get_object(self):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        # Check if user is a member or creator
        if self.request.user != project.creator and self.request.user not in project.members.all():
            raise PermissionDenied("You must be a member of this project to access the chat room.")
        
        # Ensure chat room exists
        chat_room, created = ProjectChat.objects.get_or_create(project=project)
        return project
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = context['project']
        chat_room, _ = ProjectChat.objects.get_or_create(project=project)
        context['chat_room'] = chat_room
        context['messages'] = chat_room.messages.all().select_related('sender')[:50]  # Last 50 messages
        context['is_member'] = self.request.user == project.creator or self.request.user in project.members.all()
        return context


def send_chat_message(request, pk):
    """Handle sending messages in project chat"""
    project = get_object_or_404(Project, pk=pk)
    
    # Verify user is a member
    if request.user != project.creator and request.user not in project.members.all():
        messages.error(request, 'You must be a member of this project to send messages.')
        return redirect('projects:detail', pk=pk)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            chat_room, _ = ProjectChat.objects.get_or_create(project=project)
            ProjectChatMessage.objects.create(
                chat_room=chat_room,
                sender=request.user,
                content=content
            )
            messages.success(request, 'Message sent!')
    
    return redirect('projects:chat', pk=pk)


class ProjectUpdateCreateView(LoginRequiredMixin, CreateView):
    model = ProjectUpdate
    template_name = 'projects/update_form.html'
    fields = ['content']
    
    def form_valid(self, form):
        project = get_object_or_404(Project, pk=self.kwargs['pk'])
        form.instance.project = project
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.kwargs['pk']})
