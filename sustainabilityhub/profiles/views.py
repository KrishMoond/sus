from django.views.generic import UpdateView, DetailView
from django.shortcuts import get_object_or_404
from .models import Profile
from .forms import ProfileForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profiles/detail.html'


def get_object(self):
    return get_object_or_404(Profile, user__username=self.kwargs.get('username'))


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/edit.html'


def get_object(self):
    return self.request.user.profile


def get_success_url(self):
    return reverse_lazy('profiles:detail', kwargs={'username': self.request.user.username})