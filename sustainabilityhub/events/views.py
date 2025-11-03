from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django import forms
from .models import Event


class EventListView(ListView):
    model = Event
    template_name = 'events/list.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Event.objects.all()
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search) | Q(location__icontains=search)
            )
        
        # Filter by type
        filter_type = self.request.GET.get('type')
        if filter_type:
            queryset = queryset.filter(event_type=filter_type)
            
        # Filter by time
        time_filter = self.request.GET.get('time', 'upcoming')
        if time_filter == 'upcoming':
            queryset = queryset.filter(start_date__gte=timezone.now())
        elif time_filter == 'past':
            queryset = queryset.filter(start_date__lt=timezone.now())
            
        return queryset.order_by('start_date')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'event'


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    template_name = 'events/form.html'
    fields = ['title', 'description', 'event_type', 'location', 'start_date', 'end_date', 
              'max_participants', 'image', 'is_online', 'online_link']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form
    
    def form_valid(self, form):
        form.instance.organizer = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('events:detail', kwargs={'pk': self.object.pk})


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    template_name = 'events/form.html'
    fields = ['title', 'description', 'event_type', 'location', 'start_date', 'end_date', 
              'max_participants', 'image', 'is_online', 'online_link']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_date'].widget = forms.DateInput(attrs={'type': 'date'})
        form.fields['end_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form
    
    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('events:detail', kwargs={'pk': self.object.pk})


class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    template_name = 'events/confirm_delete.html'
    success_url = reverse_lazy('events:list')
    
    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)


def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.user.is_authenticated:
        if event.max_participants and event.participant_count >= event.max_participants:
            messages.error(request, 'This event is full.')
        elif request.user not in event.participants.all():
            event.participants.add(request.user)
            messages.success(request, f'You registered for {event.title}!')
        else:
            event.participants.remove(request.user)
            messages.info(request, f'You unregistered from {event.title}.')
    return redirect('events:detail', pk=pk)
