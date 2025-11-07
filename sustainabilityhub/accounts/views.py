from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from .forms import CustomUserCreationForm
from .models import UserWarning
from notifications.utils import create_notification

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    from django.db.models import Q, Count
    
    # Get filter parameters
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', 'all')
    
    # Base queryset with counts
    users = User.objects.annotate(
        warning_count=Count('warnings', filter=Q(warnings__is_active=True)),
        forum_posts_count=Count('forum_posts', distinct=True),
        topics_count=Count('topics', distinct=True),
        created_projects_count=Count('created_projects', distinct=True),
        joined_projects_count=Count('joined_projects', distinct=True)
    ).select_related().order_by('-date_joined')
    
    # Apply search filter
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Apply status filter
    if status_filter == 'active':
        users = users.filter(is_active=True, is_superuser=False)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)
    elif status_filter == 'superuser':
        users = users.filter(is_superuser=True)
    elif status_filter == 'warned':
        users = users.filter(warning_count__gt=0)
    
    # Get statistics
    stats = {
        'total': User.objects.count(),
        'active': User.objects.filter(is_active=True, is_superuser=False).count(),
        'inactive': User.objects.filter(is_active=False).count(),
        'staff': User.objects.filter(is_staff=True).count(),
        'superuser': User.objects.filter(is_superuser=True).count(),
        'warned': User.objects.annotate(
            warning_count=Count('warnings', filter=Q(warnings__is_active=True))
        ).filter(warning_count__gt=0).count(),
    }
    
    return render(request, 'accounts/admin_users.html', {
        'users': users,
        'stats': stats,
        'search': search,
        'status_filter': status_filter
    })

@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, f'User {username} created successfully.')
            return redirect('accounts:admin_users')
    
    return render(request, 'accounts/create_user.html')

@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'User {username} deleted successfully.')
    return redirect('accounts:admin_users')

@user_passes_test(lambda u: u.is_superuser)
def warn_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        warning = UserWarning.objects.create(
            user=user,
            issued_by=request.user,
            severity=request.POST['severity'],
            reason=request.POST['reason'],
            description=request.POST['description']
        )
        
        # Notify user about warning
        create_notification(
            recipient=user,
            notification_type='warning_issued',
            title=f'{warning.get_severity_display()} Warning',
            message=f'Reason: {warning.reason}',
            url='/accounts/my-warnings/'
        )
        
        messages.success(request, f'Warning issued to {user.username}.')
        return redirect('accounts:admin_users')
    
    return render(request, 'accounts/warn_user.html', {'target_user': user})

@user_passes_test(lambda u: u.is_superuser)
def user_warnings(request, pk):
    user = get_object_or_404(User, pk=pk)
    warnings = user.warnings.all()
    return render(request, 'accounts/user_warnings.html', {'target_user': user, 'warnings': warnings})

@user_passes_test(lambda u: u.is_superuser)
def toggle_user_status(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user.is_superuser:
            messages.error(request, 'Cannot modify superuser status.')
        else:
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'deactivated'
            messages.success(request, f'User {user.username} has been {status}.')
            
            # Notify user about status change
            create_notification(
                recipient=user,
                notification_type='account_status',
                title=f'Account {status.title()}',
                message=f'Your account has been {status} by an administrator.',
                url='/'
            )
    
    return redirect('accounts:admin_users')

def my_warnings(request):
    """View for users to see their own warnings"""
    from django.utils import timezone
    
    # Mark all unviewed warnings as viewed
    request.user.warnings.filter(is_active=True, viewed_at__isnull=True).update(viewed_at=timezone.now())
    
    # Get all active warnings
    warnings = request.user.warnings.filter(is_active=True).order_by('-created_at')
    return render(request, 'accounts/my_warnings.html', {'warnings': warnings})

@user_passes_test(lambda u: u.is_superuser)
def user_detail(request, pk):
    from django.db.models import Count
    
    user = get_object_or_404(User, pk=pk)
    
    # Get user's content with counts
    topics = user.topics.all()[:10]  # Latest 10 topics
    forum_posts = user.forum_posts.all()[:10]  # Latest 10 posts
    created_projects = user.created_projects.all()[:10]  # Latest 10 created projects
    joined_projects = user.joined_projects.all()[:10]  # Latest 10 joined projects
    warnings = user.warnings.filter(is_active=True)[:10]  # Latest 10 warnings
    
    # Get comprehensive stats
    stats = {
        'topics_count': user.topics.count(),
        'forum_posts_count': user.forum_posts.count(),
        'created_projects_count': user.created_projects.count(),
        'joined_projects_count': user.joined_projects.count(),
        'warnings_count': user.warnings.filter(is_active=True).count(),
        'events_created': user.events_created.count() if hasattr(user, 'events_created') else 0,
        'resources_shared': user.resources_created.count() if hasattr(user, 'resources_created') else 0,
    }
    
    return render(request, 'accounts/user_detail.html', {
        'target_user': user,
        'topics': topics,
        'forum_posts': forum_posts,
        'created_projects': created_projects,
        'joined_projects': joined_projects,
        'warnings': warnings,
        'stats': stats,
    })