from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch, Sum
from django.db import models
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Post, PostReaction, Comment, CommentReaction, Follow, HashTag, ChallengeParticipation
from .sustainability_features import ImpactTracker
from .serializers import (
    PostSerializer, PostCreateSerializer, CommentSerializer,
    PostReactionSerializer, CommentReactionSerializer, FollowSerializer,
    HashTagSerializer
)

User = get_user_model()


# Traditional Django Views
@login_required
def community_dashboard(request):
    """Main community dashboard - challenges and fitness focused"""
    from .sustainability_features import ImpactTracker
    
    if request.method == 'POST':
        # Handle challenge creation
        content = request.POST.get('content')
        post_type = request.POST.get('post_type')
        challenge_duration = request.POST.get('challenge_duration')
        impact_category = request.POST.get('impact_category')
        carbon_impact = request.POST.get('carbon_impact')
        
        if content and post_type == 'challenge':
            post = Post.objects.create(
                author=request.user,
                content=content,
                post_type=post_type,
                challenge_duration=int(challenge_duration) if challenge_duration else None,
                impact_category=impact_category,
                carbon_impact=float(carbon_impact) if carbon_impact else None
            )
            return JsonResponse({'success': True, 'message': 'Challenge created successfully!'})
    
    # Get active challenges
    active_challenges = Post.objects.filter(
        post_type='challenge',
        challenge_duration__isnull=False
    ).select_related('author').order_by('-created_at')[:6]
    
    # Add user participation status
    if request.user.is_authenticated:
        user_participations = set(
            ChallengeParticipation.objects.filter(
                user=request.user,
                challenge_post__in=active_challenges
            ).values_list('challenge_post_id', flat=True)
        )
        for challenge in active_challenges:
            challenge.user_joined = challenge.id in user_participations
    
    # Get user's joined challenges
    user_challenges = ChallengeParticipation.objects.filter(
        user=request.user
    ).select_related('challenge_post').order_by('-joined_at')[:5]
    
    # Get user's impact stats
    user_impact = ImpactTracker.objects.filter(user=request.user).aggregate(
        total_carbon=models.Sum('amount'),
        total_actions=models.Count('id')
    )
    
    # Get leaderboard
    leaderboard = ImpactTracker.objects.values('user__username').annotate(
        total_impact=models.Sum('amount')
    ).order_by('-total_impact')[:10]
    
    context = {
        'active_challenges': active_challenges,
        'user_challenges': user_challenges,
        'user_impact': user_impact,
        'leaderboard': leaderboard,
    }
    return render(request, 'community/dashboard.html', context)


@login_required
def discover_posts(request):
    """Discover new posts and users"""
    # Get posts from users not followed
    following_users = list(request.user.community_following.values_list('following', flat=True))
    following_users.append(request.user.id)
    
    posts = Post.objects.exclude(
        author__in=following_users
    ).select_related('author').prefetch_related(
        'reactions__user', 'comments__author', 'hashtags'
    ).order_by('-created_at')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'posts': page_obj}
    return render(request, 'community/discover.html', context)


@login_required
@require_http_methods(["POST"])
def join_challenge(request, post_id):
    """Join a sustainability challenge"""

    
    post = get_object_or_404(Post, id=post_id, post_type='challenge')
    
    participation, created = ChallengeParticipation.objects.get_or_create(
        user=request.user,
        challenge_post=post
    )
    
    if created:
        post.participants_count += 1
        post.save()
        return JsonResponse({
            'action': 'joined',
            'message': 'Successfully joined challenge!',
            'participants': post.participants_count
        })
    else:
        return JsonResponse({
            'action': 'already_joined',
            'message': 'Already participating in this challenge',
            'participants': post.participants_count
        })


@login_required
def create_challenge(request):
    """Create a new challenge"""
    if request.method == 'POST':
        content = request.POST.get('content')
        challenge_duration = request.POST.get('challenge_duration')
        impact_category = request.POST.get('impact_category')
        carbon_impact = request.POST.get('carbon_impact')
        
        if content and challenge_duration:
            post = Post.objects.create(
                author=request.user,
                content=content,
                post_type='challenge',
                challenge_duration=int(challenge_duration),
                impact_category=impact_category,
                carbon_impact=float(carbon_impact) if carbon_impact else None
            )
            return JsonResponse({'success': True, 'message': 'Challenge created successfully!', 'redirect': '/community/challenges/'})
        else:
            return JsonResponse({'success': False, 'message': 'Please fill in all required fields.'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def challenges_list(request):
    """List all active challenges"""
    challenges = Post.objects.filter(
        post_type='challenge',
        challenge_duration__isnull=False
    ).select_related('author').prefetch_related(
        'participants', 'hashtags'
    ).order_by('-created_at')
    
    # Add user participation status
    if request.user.is_authenticated:
        user_participations = set(
            ChallengeParticipation.objects.filter(
                user=request.user,
                challenge_post__in=challenges
            ).values_list('challenge_post_id', flat=True)
        )
        for challenge in challenges:
            challenge.user_joined = challenge.id in user_participations
    
    context = {'challenges': challenges}
    return render(request, 'community/challenges.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_post_reaction(request, post_id):
    """Toggle reaction on a post"""
    post = get_object_or_404(Post, id=post_id)
    reaction_type = request.POST.get('reaction_type', 'like')
    
    reaction, created = PostReaction.objects.get_or_create(
        post=post,
        user=request.user,
        defaults={'reaction_type': reaction_type}
    )
    
    if not created:
        if reaction.reaction_type == reaction_type:
            reaction.delete()
            return JsonResponse({'action': 'removed', 'total': post.total_reactions})
        else:
            reaction.reaction_type = reaction_type
            reaction.save()
    
    return JsonResponse({
        'action': 'added' if created else 'updated',
        'reaction_type': reaction_type,
        'total': post.total_reactions
    })


@login_required
@require_http_methods(["POST"])
def toggle_follow(request, user_id):
    """Toggle following a user"""
    user_to_follow = get_object_or_404(User, id=user_id)
    
    if user_to_follow == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        follow.delete()
        return JsonResponse({'action': 'unfollowed'})
    
    return JsonResponse({'action': 'followed'})


# DRF API ViewSets
class PostViewSet(viewsets.ModelViewSet):
    """API ViewSet for posts"""
    queryset = Post.objects.all().select_related('author').prefetch_related(
        'reactions__user', 'comments__author', 'hashtags'
    ).order_by('-is_pinned', '-created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by hashtag
        hashtag = self.request.query_params.get('hashtag')
        if hashtag:
            queryset = queryset.filter(hashtags__name__icontains=hashtag)
        
        # Filter by post type
        post_type = self.request.query_params.get('type')
        if post_type:
            queryset = queryset.filter(post_type=post_type)
        
        # Filter by author
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def react(self, request, pk=None):
        """Add or update reaction to a post"""
        post = self.get_object()
        reaction_type = request.data.get('reaction_type', 'like')
        
        reaction, created = PostReaction.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                return Response({'action': 'removed'})
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
        
        serializer = PostReactionSerializer(reaction, context={'request': request})
        return Response({
            'action': 'added' if created else 'updated',
            'reaction': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def feed(self, request):
        """Get personalized feed for authenticated user"""
        following_users = request.user.following.values_list('following', flat=True)
        queryset = self.get_queryset().filter(
            Q(author__in=following_users) | Q(author=request.user)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def discover(self, request):
        """Get posts for discovery (from non-followed users)"""
        if request.user.is_authenticated:
            following_users = list(request.user.following.values_list('following', flat=True))
            following_users.append(request.user.id)
            queryset = self.get_queryset().exclude(author__in=following_users)
        else:
            queryset = self.get_queryset()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join_challenge(self, request, pk=None):
        """Join a sustainability challenge"""
        post = self.get_object()
        
        if post.post_type != 'challenge':
            return Response({'error': 'This is not a challenge post'}, status=status.HTTP_400_BAD_REQUEST)
        
        participation, created = ChallengeParticipation.objects.get_or_create(
            user=request.user,
            challenge_post=post
        )
        
        if created:
            post.participants_count += 1
            post.save()
            return Response({'message': 'Successfully joined challenge!', 'participants': post.participants_count})
        else:
            return Response({'message': 'Already participating in this challenge', 'participants': post.participants_count})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complete_challenge(self, request, pk=None):
        """Mark challenge as completed with proof"""
        post = self.get_object()
        
        try:
            participation = ChallengeParticipation.objects.get(
                user=request.user,
                challenge_post=post
            )
        except ChallengeParticipation.DoesNotExist:
            return Response({'error': 'You are not participating in this challenge'}, status=status.HTTP_400_BAD_REQUEST)
        
        participation.completed = True
        participation.impact_achieved = request.data.get('impact_achieved')
        participation.save()
        
        return Response({'message': 'Challenge completed successfully!'})


class CommentViewSet(viewsets.ModelViewSet):
    """API ViewSet for comments"""
    queryset = Comment.objects.all().select_related('author', 'post').prefetch_related('reactions__user')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def react(self, request, pk=None):
        """Add or update reaction to a comment"""
        comment = self.get_object()
        reaction_type = request.data.get('reaction_type', 'like')
        
        reaction, created = CommentReaction.objects.get_or_create(
            comment=comment,
            user=request.user,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                return Response({'action': 'removed'})
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
        
        serializer = CommentReactionSerializer(reaction, context={'request': request})
        return Response({
            'action': 'added' if created else 'updated',
            'reaction': serializer.data
        })


class FollowViewSet(viewsets.ModelViewSet):
    """API ViewSet for follow relationships"""
    queryset = Follow.objects.all().select_related('follower', 'following')
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by follower
        follower = self.request.query_params.get('follower')
        if follower:
            queryset = queryset.filter(follower__username=follower)
        
        # Filter by following
        following = self.request.query_params.get('following')
        if following:
            queryset = queryset.filter(following__username=following)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """Toggle follow status for a user"""
        following_id = request.data.get('following_id')
        if not following_id:
            return Response({'error': 'following_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_to_follow = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if user_to_follow == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        follow, created = Follow.objects.get_or_create(
            follower=request.user,
            following=user_to_follow
        )
        
        if not created:
            follow.delete()
            return Response({'action': 'unfollowed'})
        
        serializer = self.get_serializer(follow)
        return Response({
            'action': 'followed',
            'follow': serializer.data
        })


class HashTagViewSet(viewsets.ReadOnlyModelViewSet):
    """API ViewSet for hashtags"""
    queryset = HashTag.objects.all().annotate(
        post_count=Count('posts')
    ).order_by('-post_count')
    serializer_class = HashTagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending hashtags"""
        queryset = self.get_queryset().filter(post_count__gt=0)[:20]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def challenges(self, request):
        """Get active challenges"""
        from .models import Post
        challenges = Post.objects.filter(
            post_type='challenge',
            challenge_duration__isnull=False
        ).order_by('-created_at')
        
        from .serializers import PostSerializer
        serializer = PostSerializer(challenges, many=True, context={'request': request})
        return Response(serializer.data)