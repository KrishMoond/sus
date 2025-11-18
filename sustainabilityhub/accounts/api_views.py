from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from .serializers import (
    UserRegistrationSerializer, UserProfileSerializer, UserBasicSerializer,
    UserWarningSerializer, PasswordChangeSerializer, LoginSerializer,
    UserSearchSerializer
)
from .models import UserWarning
from .permissions import get_user_role, assign_user_role, CanManageUsers

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """API ViewSet for user management"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action in ['list', 'search']:
            return UserSearchSerializer
        return UserProfileSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(bio__icontains=search)
            )
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            if role == 'admin':
                queryset = queryset.filter(is_staff=True)
            elif role == 'moderator':
                queryset = queryset.filter(groups__name='Moderators')
            elif role == 'verified':
                queryset = queryset.filter(groups__name='Verified Users')
        
        return queryset.select_related().prefetch_related('groups')
    
    def perform_create(self, serializer):
        """Create new user account"""
        user = serializer.save()
        # Create auth token
        Token.objects.create(user=user)
        return user
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanManageUsers])
    def assign_role(self, request, pk=None):
        """Assign role to user (admin only)"""
        user = self.get_object()
        role = request.data.get('role')
        
        if not role:
            return Response(
                {'error': 'Role is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = assign_user_role(user, role)
        if success:
            return Response({
                'message': f'Role {role} assigned to {user.username}',
                'user': UserBasicSerializer(user, context={'request': request}).data
            })
        else:
            return Response(
                {'error': 'Invalid role'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get user statistics"""
        user = self.get_object()
        
        stats = {
            'projects_created': user.created_projects.count(),
            'projects_joined': user.joined_projects.count(),
            'forum_posts': user.forum_posts.count(),
            'community_posts': getattr(user, 'community_posts', user.social_posts).count(),
            'events_created': user.created_events.count(),
            'followers_count': user.followers.count(),
            'following_count': user.following.count(),
            'warnings_count': user.warnings.filter(is_active=True).count(),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search users"""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        
        users = self.get_queryset().filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )[:20]
        
        serializer = UserSearchSerializer(users, many=True, context={'request': request})
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """User registration endpoint"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user, context={'request': request}).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_user(request):
    """User login endpoint"""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Log the user in for session-based auth
        login(request, user)
        
        return Response({
            'user': UserProfileSerializer(user, context={'request': request}).data,
            'token': token.key,
            'message': 'Login successful'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_user(request):
    """User logout endpoint"""
    try:
        # Delete the token
        request.user.auth_token.delete()
    except:
        pass
    
    # Logout from session
    logout(request)
    
    return Response({'message': 'Logout successful'})


class UserWarningViewSet(viewsets.ModelViewSet):
    """API ViewSet for user warnings"""
    queryset = UserWarning.objects.all()
    serializer_class = UserWarningSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Users can only see their own warnings unless they're staff
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by active status
        active = self.request.query_params.get('active')
        if active is not None:
            queryset = queryset.filter(is_active=active.lower() == 'true')
        
        return queryset.select_related('user', 'issued_by')
    
    def perform_create(self, serializer):
        """Create warning (staff only)"""
        if not self.request.user.is_staff:
            raise permissions.PermissionDenied("Only staff can issue warnings")
        serializer.save(issued_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark warning as viewed"""
        warning = self.get_object()
        
        # Users can only mark their own warnings as viewed
        if warning.user != request.user and not request.user.is_staff:
            raise permissions.PermissionDenied()
        
        if not warning.viewed_at:
            warning.viewed_at = timezone.now()
            warning.save()
        
        return Response({'message': 'Warning marked as viewed'})
    
    @action(detail=True, methods=['post'])
    def submit_justification(self, request, pk=None):
        """Submit justification for warning"""
        warning = self.get_object()
        
        # Users can only submit justification for their own warnings
        if warning.user != request.user:
            raise permissions.PermissionDenied()
        
        justification = request.data.get('justification', '').strip()
        if not justification:
            return Response(
                {'error': 'Justification is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        warning.justification = justification
        warning.justification_submitted_at = timezone.now()
        warning.save()
        
        return Response({'message': 'Justification submitted successfully'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard_stats(request):
    """Get dashboard statistics for current user"""
    user = request.user
    
    stats = {
        'projects': {
            'created': user.created_projects.count(),
            'joined': user.joined_projects.count(),
            'active': user.created_projects.filter(status='active').count(),
        },
        'community': {
            'posts': getattr(user, 'community_posts', user.social_posts).count(),
            'comments': getattr(user, 'community_comments', user.comments).count(),
            'followers': user.followers.count(),
            'following': user.following.count(),
        },
        'forum': {
            'topics': user.topics.count(),
            'posts': user.forum_posts.count(),
        },
        'events': {
            'created': user.created_events.count(),
            'attending': user.event_attendees.count(),
        },
        'warnings': {
            'active': user.warnings.filter(is_active=True).count(),
            'total': user.warnings.count(),
        }
    }
    
    return Response(stats)