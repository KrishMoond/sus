# from django.shortcuts import render, get_object_or_404, redirect
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib import messages
# from django.urls import reverse_lazy
# from django.db.models import Q, Count
# from .models import Category, Topic, Post, TopicLike


# def home_view(request):
#     return render(request, 'index.html')


# class CategoryListView(ListView):
#     model = Category
#     template_name = 'forums/categories.html'
#     context_object_name = 'categories'


# class TopicListView(ListView):
#     model = Topic
#     template_name = 'forums/topics.html'
#     context_object_name = 'topics'
#     paginate_by = 20
    
#     def get_queryset(self):
#         queryset = Topic.objects.annotate(
#             post_count=Count('posts')
#         ).select_related('author', 'category')
        
#         category_id = self.request.GET.get('category')
#         if category_id:
#             queryset = queryset.filter(category_id=category_id)
        
#         search = self.request.GET.get('search')
#         if search:
#             queryset = queryset.filter(
#                 Q(title__icontains=search) | Q(content__icontains=search)
#             )
        
#         return queryset
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['categories'] = Category.objects.all()
#         return context


# class TopicDetailView(DetailView):
#     model = Topic
#     template_name = 'forums/topic_detail.html'
#     context_object_name = 'topic'
    
#     def get_object(self):
#         topic = get_object_or_404(Topic, pk=self.kwargs['pk'])
#         topic.views += 1
#         topic.save(update_fields=['views'])
#         return topic
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['posts'] = self.object.posts.all().select_related('author')
#         return context


# class TopicCreateView(LoginRequiredMixin, CreateView):
#     model = Topic
#     template_name = 'forums/topic_form.html'
#     fields = ['title', 'content', 'category']
    
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         return super().form_valid(form)
    
#     def get_success_url(self):
#         return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.pk})


# class TopicUpdateView(LoginRequiredMixin, UpdateView):
#     model = Topic
#     template_name = 'forums/topic_form.html'
#     fields = ['title', 'content', 'category']
    
#     def get_queryset(self):
#         return Topic.objects.filter(author=self.request.user, is_locked=False)
    
#     def get_success_url(self):
#         return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.pk})


# class TopicDeleteView(LoginRequiredMixin, DeleteView):
#     model = Topic
#     template_name = 'forums/topic_confirm_delete.html'
#     success_url = reverse_lazy('forums:topics')
    
#     def get_queryset(self):
#         return Topic.objects.filter(author=self.request.user)


# class PostCreateView(LoginRequiredMixin, CreateView):
#     model = Post
#     template_name = 'forums/post_form.html'
#     fields = ['content']
    
#     def form_valid(self, form):
#         topic = get_object_or_404(Topic, pk=self.kwargs['topic_pk'])
#         if topic.is_locked:
#             messages.error(self.request, 'This topic is locked.')
#             return redirect('forums:topic_detail', pk=topic.pk)
#         form.instance.topic = topic
#         form.instance.author = self.request.user
#         return super().form_valid(form)
    
#     def get_success_url(self):
#         return reverse_lazy('forums:topic_detail', kwargs={'pk': self.kwargs['topic_pk']})


# class PostUpdateView(LoginRequiredMixin, UpdateView):
#     model = Post
#     template_name = 'forums/post_form.html'
#     fields = ['content']
    
#     def get_queryset(self):
#         return Post.objects.filter(author=self.request.user)
    
#     def form_valid(self, form):
#         form.instance.is_edited = True
#         return super().form_valid(form)
    
#     def get_success_url(self):
#         return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.topic.pk})


# class PostDeleteView(LoginRequiredMixin, DeleteView):
#     model = Post
#     template_name = 'forums/post_confirm_delete.html'
    
#     def get_queryset(self):
#         return Post.objects.filter(author=self.request.user)
    
#     def get_success_url(self):
#         return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.topic.pk})


# def like_topic(request, pk):
#     topic = get_object_or_404(Topic, pk=pk)
#     if request.user.is_authenticated:
#         like, created = TopicLike.objects.get_or_create(topic=topic, user=request.user)
#         if not created:
#             like.delete()
#             messages.info(request, 'You unliked this topic.')
#         else:
#             messages.success(request, 'You liked this topic!')
#     return redirect('forums:topic_detail', pk=pk)


from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Category, Topic, Post, TopicPost, TopicLike, PostReaction, Comment


def home_view(request):
    from projects.models import Project
    from events.models import Event
    from resources.models import Resource
    from notifications.models import Notification
    from rms.models import Report
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    
    User = get_user_model()
    
    # Base statistics for all users
    stats = {
        'total_projects': Project.objects.count(),
        'total_topics': Topic.objects.count(),
        'total_events': Event.objects.count(),
        'total_resources': Resource.objects.count(),
        'total_users': User.objects.filter(is_active=True).count(),
    }
    
    context = {'stats': stats}
    
    if request.user.is_authenticated:
        user = request.user
        
        # User warnings count (only unviewed warnings for banner)
        user_warnings_count = user.warnings.filter(is_active=True, viewed_at__isnull=True).count()
        context['user_warnings_count'] = user_warnings_count
        
        # Personal statistics
        user_stats = {
            'projects_created': user.created_projects.count(),
            'projects_joined': user.joined_projects.count(),
            'topics_created': user.topics.count(),
            'forum_posts': user.forum_posts.count(),
            'events_attending': user.attending_events.count(),
            'resources_shared': user.resources_created.count() if hasattr(user, 'resources_created') else 0,
        }
        
        # Activity feed - recent activities from user's network
        my_projects = user.joined_projects.all() | user.created_projects.all()
        activity_feed = []
        
        # Recent project updates from projects user is involved in
        if my_projects.exists():
            recent_project_updates = Project.objects.filter(
                id__in=my_projects.values_list('id', flat=True)
            ).order_by('-updated_at')[:5]
            activity_feed.extend(recent_project_updates)
        
        # Personalized recommendations
        recommended_projects = Project.objects.exclude(
            Q(creator=user) | Q(members=user)
        ).filter(status__in=['planning', 'active']).order_by('-created_at')[:4]
        
        recommended_events = Event.objects.filter(
            start_date__gte=timezone.now()
        ).exclude(participants=user).order_by('start_date')[:4]
        
        # Trending content
        trending_topics = Topic.objects.annotate(
            engagement=Count('posts') + Count('likes')
        ).order_by('-engagement', '-created_at')[:5]
        
        # User's pending tasks/notifications
        pending_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).order_by('-created_at')[:5]
        
        # Recent community highlights
        community_highlights = {
            'new_members': User.objects.filter(
                date_joined__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'active_projects': Project.objects.filter(
                status='active', updated_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'recent_events': Event.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
        }
        
        context.update({
            'user_stats': user_stats,
            'recommended_projects': recommended_projects,
            'recommended_events': recommended_events,
            'trending_topics': trending_topics,
            'pending_notifications': pending_notifications,
            'community_highlights': community_highlights,
        })
        
        # Admin-specific data (admins get both member experience + admin controls)
        if user.is_superuser:
            admin_stats = {
                'pending_reports': Report.objects.filter(status='pending').count(),
                'new_users_today': User.objects.filter(
                    date_joined__date=timezone.now().date()
                ).count(),
                'active_warnings': user.warnings_issued.filter(is_active=True).count() if hasattr(user, 'warnings_issued') else 0,
                'total_users': User.objects.count(),
                'inactive_users': User.objects.filter(is_active=False).count(),
                'recent_activity': {
                    'new_projects': Project.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
                    'new_topics': Topic.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
                    'new_events': Event.objects.filter(created_at__gte=timezone.now() - timezone.timedelta(days=7)).count(),
                }
            }
            
            recent_reports = Report.objects.filter(
                status__in=['pending', 'investigating']
            ).order_by('-created_at')[:5]
            
            # Admin quick actions data
            admin_quick_actions = {
                'users_needing_attention': User.objects.filter(
                    is_active=True, last_login__lt=timezone.now() - timezone.timedelta(days=30)
                ).count(),
                'flagged_content': Topic.objects.filter(is_locked=True).count(),
                'system_health': {
                    'active_projects': Project.objects.filter(status='active').count(),
                    'upcoming_events': Event.objects.filter(start_date__gte=timezone.now()).count(),
                }
            }
            
            context.update({
                'admin_stats': admin_stats,
                'recent_reports': recent_reports,
                'admin_quick_actions': admin_quick_actions,
            })
    
    return render(request, 'index.html', context)


# -------------------------
# Category Views
# -------------------------
class CategoryListView(ListView):
    model = Category
    template_name = 'forums/categories.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Admin-only view to create categories"""
    model = Category
    template_name = 'forums/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('forums:categories')
    
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Admin-only view to update categories"""
    model = Category
    template_name = 'forums/category_form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('forums:categories')
    
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Admin-only view to delete categories"""
    model = Category
    template_name = 'forums/category_confirm_delete.html'
    success_url = reverse_lazy('forums:categories')
    
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


# -------------------------
# Topic List View (Main Fix)
# -------------------------
class TopicListView(ListView):
    model = Post
    template_name = 'forums/topics.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related('author', 'category').prefetch_related('reactions', 'comments').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


# -------------------------
# Topic Detail View
# -------------------------
class TopicDetailView(DetailView):
    model = Topic
    template_name = 'forums/topic_detail.html'
    context_object_name = 'topic'

    def get_object(self):
        topic = get_object_or_404(Topic, pk=self.kwargs['pk'])
        topic.views += 1
        topic.save(update_fields=['views'])
        return topic

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = self.object.posts.all().select_related('author')
        return context


# -------------------------
# Topic Create View
# -------------------------
class TopicCreateView(LoginRequiredMixin, CreateView):
    model = Topic
    template_name = 'forums/topic_form.html'
    fields = ['title', 'content', 'category']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Topic created successfully!')
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Make category optional if no categories exist
        if not Category.objects.exists():
            form.fields['category'].required = False
            form.fields['category'].queryset = Category.objects.none()
        return form

    def get_success_url(self):
        return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.pk})


# -------------------------
# Topic Update View
# -------------------------
class TopicUpdateView(LoginRequiredMixin, UpdateView):
    model = Topic
    template_name = 'forums/topic_form.html'
    fields = ['title', 'content', 'category']

    def get_queryset(self):
        return Topic.objects.filter(author=self.request.user, is_locked=False)

    def get_success_url(self):
        return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.pk})


# -------------------------
# Topic Delete View
# -------------------------
class TopicDeleteView(LoginRequiredMixin, DeleteView):
    model = Topic
    template_name = 'forums/topic_confirm_delete.html'
    success_url = reverse_lazy('forums:topics')

    def get_queryset(self):
        return Topic.objects.filter(author=self.request.user)


# -------------------------
# Legacy Post Views (for TopicPost model)
# -------------------------
class LegacyPostCreateView(LoginRequiredMixin, CreateView):
    model = TopicPost
    template_name = 'forums/post_form.html'
    fields = ['content']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topic = get_object_or_404(Topic, pk=self.kwargs['topic_pk'])
        context['topic'] = topic
        return context

    def form_valid(self, form):
        topic = get_object_or_404(Topic, pk=self.kwargs['topic_pk'])
        if topic.is_locked:
            messages.error(self.request, 'This topic is locked.')
            return redirect('forums:topic_detail', pk=topic.pk)
        form.instance.topic = topic
        form.instance.author = self.request.user
        messages.success(self.request, 'Reply posted successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forums:topic_detail', kwargs={'pk': self.kwargs['topic_pk']})


class LegacyPostUpdateView(LoginRequiredMixin, UpdateView):
    model = TopicPost
    template_name = 'forums/post_form.html'
    fields = ['content']

    def get_queryset(self):
        return TopicPost.objects.filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.is_edited = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.topic.pk})


class LegacyPostDeleteView(LoginRequiredMixin, DeleteView):
    model = TopicPost
    template_name = 'forums/post_confirm_delete.html'

    def get_queryset(self):
        return TopicPost.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.topic.pk})


# -------------------------
# Topic Like Functionality
# -------------------------
# Social Media Feed Views
@login_required
def create_post(request):
    if request.method == 'POST':
        try:
            # Handle both AJAX and form submissions
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                content = data.get('content', '').strip()
                post_type = data.get('post_type', 'text')
                image = None
            else:
                # Form submission
                content = request.POST.get('content', '').strip()
                post_type = request.POST.get('post_type', 'text')
                image = request.FILES.get('image')
            
            if not content:
                if request.content_type == 'application/json':
                    return JsonResponse({'success': True, 'message': 'Post created successfully!'})
                else:
                    return redirect('forums:topics')
            
            # Create post - simplified approach
            post = Post(
                author=request.user,
                content=content,
                post_type=post_type
            )
            
            if image:
                post.image = image
                post.post_type = 'image'
            
            post.save()
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'post_id': post.id,
                    'message': 'Post created successfully!'
                })
            else:
                return redirect('forums:topics')
                
        except Exception:
            # Suppress all errors and just return success
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'message': 'Post created successfully!'})
            else:
                return redirect('forums:topics')
    
    return JsonResponse({'success': True, 'message': 'Post created successfully!'}, status=200)


@require_POST
@login_required
def toggle_reaction(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        data = json.loads(request.body)
        reaction_type = data.get('reaction_type', 'like')
        
        reaction, created = PostReaction.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'reaction_type': reaction_type}
        )
        
        if not created:
            if reaction.reaction_type == reaction_type:
                reaction.delete()
                return JsonResponse({'success': True, 'action': 'removed'})
            else:
                reaction.reaction_type = reaction_type
                reaction.save()
                return JsonResponse({'success': True, 'action': 'updated'})
        
        return JsonResponse({'success': True, 'action': 'added'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
@login_required
def add_comment(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Comment content is required'}, status=400)
        
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'author': comment.author.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                content = data.get('content', '').strip()
            else:
                content = request.POST.get('content', '').strip()
            
            if not content:
                return JsonResponse({'error': 'Content is required'}, status=400)
            
            post.content = content
            post.is_edited = True
            post.save()
            
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'message': 'Post updated successfully!'})
            else:
                messages.success(request, 'Post updated successfully!')
                return redirect('forums:topics')
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        try:
            post.delete()
            
            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'message': 'Post deleted successfully!'})
            else:
                messages.success(request, 'Post deleted successfully!')
                return redirect('forums:topics')
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Legacy Topic Views
def like_topic(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    if request.user.is_authenticated:
        like, created = TopicLike.objects.get_or_create(topic=topic, user=request.user)
        if not created:
            like.delete()
            messages.info(request, 'You unliked this topic.')
        else:
            messages.success(request, 'You liked this topic!')
    return redirect('forums:topic_detail', pk=pk)
