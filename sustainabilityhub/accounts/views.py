from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta
from .forms import CustomUserCreationForm
from projects.models import Project
from events.models import Event
from forums.models import Topic, Post, Category
from resources.models import Resource
from notifications.models import Notification
from messaging.models import Conversation, Message

User = get_user_model()


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            # Automatically log the user in after registration
            from django.contrib.auth import login as auth_login
            auth_login(request, user)
            messages.success(request, f'Welcome to Sustainability Hub, {username}! Your account has been created.')
            return redirect('home')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    from django.contrib.auth.forms import AuthenticationForm
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # Debug: Check if form data is received
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            form = AuthenticationForm()
            return render(request, 'accounts/login.html', {'form': form})
        
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            # Ensure user is active
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Your account is inactive. Please contact support.')
        else:
            # Show specific form errors
            if 'username' in form.errors:
                for error in form.errors['username']:
                    messages.error(request, f'Username: {error}')
            elif 'password' in form.errors:
                for error in form.errors['password']:
                    messages.error(request, f'Password: {error}')
            elif form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, str(error))
            else:
                messages.error(request, 'Invalid username or password. Please check your credentials and try again.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def is_admin(user):
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with community statistics and management"""
    
    # User Statistics
    total_users = User.objects.count()
    active_users_30d = User.objects.filter(last_login__gte=datetime.now() - timedelta(days=30)).count()
    new_users_7d = User.objects.filter(date_joined__gte=datetime.now() - timedelta(days=7)).count()
    
    # Content Statistics
    total_projects = Project.objects.count()
    total_events = Event.objects.count()
    total_topics = Topic.objects.count()
    total_posts = Post.objects.count()
    total_resources = Resource.objects.count()
    
    # Activity Statistics
    recent_projects = Project.objects.select_related('creator').order_by('-created_at')[:10]
    recent_events = Event.objects.select_related('organizer').order_by('-created_at')[:10]
    recent_topics = Topic.objects.select_related('author').order_by('-created_at')[:10]
    
    # User Activity
    most_active_users = User.objects.annotate(
        topics_count=Count('topics'),
        projects_count=Count('created_projects'),
        events_count=Count('organized_events')
    ).order_by('-topics_count', '-projects_count')[:10]
    
    # Recent Activity
    recent_notifications = Notification.objects.order_by('-created_at')[:20]
    
    context = {
        'total_users': total_users,
        'active_users_30d': active_users_30d,
        'new_users_7d': new_users_7d,
        'total_projects': total_projects,
        'total_events': total_events,
        'total_topics': total_topics,
        'total_posts': total_posts,
        'total_resources': total_resources,
        'recent_projects': recent_projects,
        'recent_events': recent_events,
        'recent_topics': recent_topics,
        'most_active_users': most_active_users,
        'recent_notifications': recent_notifications,
    }
    
    return render(request, 'admin/dashboard.html', context)
