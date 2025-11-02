from django.views.generic import UpdateView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Profile
from .forms import ProfileForm, UserForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/detail.html'
    
    def get_object(self):
        return get_object_or_404(Profile, user__username=self.kwargs.get('username'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = context['profile'].user
        context['user_stats'] = {
            'projects_created': profile_user.created_projects.count(),
            'projects_joined': profile_user.joined_projects.count(),
            'events_attending': profile_user.attending_events.count() if hasattr(profile_user, 'attending_events') else 0,
        }
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/edit.html'
    
    def get_object(self):
        return self.request.user.profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = UserForm(instance=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile_form = ProfileForm(request.POST, instance=self.object)
        user_form = UserForm(request.POST, request.FILES, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(self.get_success_url())
        
        return self.render_to_response({
            'form': profile_form,
            'user_form': user_form,
            'object': self.object
        })
    
    def get_success_url(self):
        return reverse_lazy('profiles:detail', kwargs={'username': self.request.user.username})