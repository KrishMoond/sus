from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from forums.models import Topic
from projects.models import Project
from events.models import Event
from resources.models import Resource
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def global_search(request):
    query = request.GET.get('q', '').strip()
    results = {
        'topics': [],
        'projects': [],
        'events': [],
        'resources': [],
        'users': [],
    }
    
    if query:
        # Search topics
        results['topics'] = Topic.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        ).select_related('author', 'category')[:10]
        
        # Search projects
        results['projects'] = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__icontains=query)
        ).select_related('creator')[:10]
        
        # Search events
        results['events'] = Event.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query)
        ).select_related('organizer')[:10]
        
        # Search resources
        results['resources'] = Resource.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(tags__icontains=query)
        ).select_related('author')[:10]
        
        # Search users
        results['users'] = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).filter(is_active=True)[:10]
    
    return render(request, 'search_results.html', {'query': query, 'results': results})
