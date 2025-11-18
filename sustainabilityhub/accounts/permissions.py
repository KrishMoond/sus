from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.author == request.user or obj.creator == request.user


class IsModeratorOrReadOnly(permissions.BasePermission):
    """
    Custom permission for moderators to edit content.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.groups.filter(name='Moderators').exists()
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission for admins only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user.is_authenticated and request.user.is_staff


class CanManageUsers(permissions.BasePermission):
    """
    Permission for user management operations.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or
            request.user.has_perm('accounts.can_manage_users')
        )


class CanModerateContent(permissions.BasePermission):
    """
    Permission for content moderation.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or
            request.user.has_perm('accounts.can_moderate_content') or
            request.user.groups.filter(name='Moderators').exists()
        )


def create_user_groups():
    """Create default user groups with permissions"""
    
    # Create groups
    admin_group, created = Group.objects.get_or_create(name='Administrators')
    moderator_group, created = Group.objects.get_or_create(name='Moderators')
    community_leader_group, created = Group.objects.get_or_create(name='Community Leaders')
    verified_user_group, created = Group.objects.get_or_create(name='Verified Users')
    
    # Get content types
    from django.contrib.auth import get_user_model
    from forums.models import Topic, Post as ForumPost
    from projects.models import Project
    from events.models import Event
    from community.models import Post as CommunityPost
    
    User = get_user_model()
    user_ct = ContentType.objects.get_for_model(User)
    topic_ct = ContentType.objects.get_for_model(Topic)
    forum_post_ct = ContentType.objects.get_for_model(ForumPost)
    project_ct = ContentType.objects.get_for_model(Project)
    event_ct = ContentType.objects.get_for_model(Event)
    community_post_ct = ContentType.objects.get_for_model(CommunityPost)
    
    # Create custom permissions
    permissions_to_create = [
        ('can_manage_users', 'Can manage users', user_ct),
        ('can_moderate_content', 'Can moderate content', user_ct),
        ('can_ban_users', 'Can ban users', user_ct),
        ('can_feature_content', 'Can feature content', user_ct),
        ('can_pin_posts', 'Can pin posts', community_post_ct),
        ('can_create_events', 'Can create events', event_ct),
        ('can_manage_projects', 'Can manage all projects', project_ct),
    ]
    
    for codename, name, content_type in permissions_to_create:
        Permission.objects.get_or_create(
            codename=codename,
            name=name,
            content_type=content_type
        )
    
    # Assign permissions to groups
    
    # Administrators - Full access
    admin_permissions = Permission.objects.all()
    admin_group.permissions.set(admin_permissions)
    
    # Moderators - Content moderation
    moderator_permissions = Permission.objects.filter(
        codename__in=[
            'can_moderate_content',
            'can_feature_content',
            'can_pin_posts',
            'delete_topic',
            'delete_post',
            'change_topic',
            'change_post',
        ]
    )
    moderator_group.permissions.set(moderator_permissions)
    
    # Community Leaders - Enhanced content creation
    leader_permissions = Permission.objects.filter(
        codename__in=[
            'can_create_events',
            'can_feature_content',
            'can_pin_posts',
            'add_project',
            'change_project',
        ]
    )
    community_leader_group.permissions.set(leader_permissions)
    
    # Verified Users - Basic enhanced permissions
    verified_permissions = Permission.objects.filter(
        codename__in=[
            'add_project',
            'add_event',
            'add_topic',
            'add_post',
        ]
    )
    verified_user_group.permissions.set(verified_permissions)


def assign_user_role(user, role):
    """Assign a role to a user"""
    # Remove from all groups first
    user.groups.clear()
    
    role_group_mapping = {
        'admin': 'Administrators',
        'moderator': 'Moderators',
        'community_leader': 'Community Leaders',
        'verified_user': 'Verified Users',
    }
    
    group_name = role_group_mapping.get(role)
    if group_name:
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            return True
        except Group.DoesNotExist:
            return False
    return False


def get_user_role(user):
    """Get the primary role of a user"""
    if user.is_superuser:
        return 'superuser'
    elif user.groups.filter(name='Administrators').exists():
        return 'admin'
    elif user.groups.filter(name='Moderators').exists():
        return 'moderator'
    elif user.groups.filter(name='Community Leaders').exists():
        return 'community_leader'
    elif user.groups.filter(name='Verified Users').exists():
        return 'verified_user'
    else:
        return 'user'


def user_has_role(user, role):
    """Check if user has a specific role"""
    return get_user_role(user) == role


def user_can_moderate(user):
    """Check if user can moderate content"""
    return user.is_staff or user.groups.filter(
        name__in=['Administrators', 'Moderators']
    ).exists()