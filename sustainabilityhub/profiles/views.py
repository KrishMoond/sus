from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Profile, Follow, Bookmark, Activity
from django.views.decorators.http import require_POST

User = get_user_model()

def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    stats = {
        'followers': user.followers.count(),
        'following': user.following.count(),
        'topics': user.topics.count(),
        'projects': user.created_projects.count(),
    }
    
    activities = Activity.objects.filter(user=user).select_related('user')[:20]
    
    return render(request, 'profiles/detail.html', {
        'profile_user': user,
        'profile': profile,
        'is_following': is_following,
        'stats': stats,
        'activities': activities,
    })

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        profile.bio = request.POST.get('bio', '')
        profile.location = request.POST.get('location', '')
        profile.website = request.POST.get('website', '')
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profiles:detail', username=request.user.username)
    
    return render(request, 'profiles/edit.html', {'profile': profile})

@login_required
@require_POST
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        Activity.objects.create(
            user=request.user,
            activity_type='user_followed',
            description=f'Started following {user_to_follow.username}'
        )
        return JsonResponse({'status': 'followed', 'message': f'Now following {user_to_follow.username}'})
    else:
        follow.delete()
        return JsonResponse({'status': 'unfollowed', 'message': f'Unfollowed {user_to_follow.username}'})

@login_required
@require_POST
def toggle_bookmark(request):
    content_type = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    
    if not content_type or not object_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=int(object_id)
    )
    
    if not created:
        bookmark.delete()
        return JsonResponse({'status': 'removed', 'message': 'Bookmark removed'})
    
    return JsonResponse({'status': 'added', 'message': 'Bookmark added'})

@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('user')
    
    # Organize bookmarks by type
    organized = {
        'topics': [],
        'projects': [],
        'events': [],
        'resources': [],
    }
    
    for bookmark in bookmarks:
        if bookmark.content_type == 'topic':
            from forums.models import Topic
            try:
                obj = Topic.objects.get(pk=bookmark.object_id)
                organized['topics'].append(obj)
            except Topic.DoesNotExist:
                bookmark.delete()
        elif bookmark.content_type == 'project':
            from projects.models import Project
            try:
                obj = Project.objects.get(pk=bookmark.object_id)
                organized['projects'].append(obj)
            except Project.DoesNotExist:
                bookmark.delete()
        elif bookmark.content_type == 'event':
            from events.models import Event
            try:
                obj = Event.objects.get(pk=bookmark.object_id)
                organized['events'].append(obj)
            except Event.DoesNotExist:
                bookmark.delete()
        elif bookmark.content_type == 'resource':
            from resources.models import Resource
            try:
                obj = Resource.objects.get(pk=bookmark.object_id)
                organized['resources'].append(obj)
            except Resource.DoesNotExist:
                bookmark.delete()
    
    return render(request, 'profiles/bookmarks.html', {'bookmarks': organized})

@login_required
def activity_feed(request):
    # Get activities from users the current user follows
    following_users = request.user.following.values_list('following', flat=True)
    activities = Activity.objects.filter(user__in=following_users).select_related('user').order_by('-created_at')[:50]
    
    return render(request, 'profiles/activity_feed.html', {'activities': activities})
