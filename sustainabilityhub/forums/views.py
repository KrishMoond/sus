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
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.utils import timezone
from .models import Category, Topic, Post, TopicLike


def home_view(request):
    from projects.models import Project
    from events.models import Event
    from resources.models import Resource
    from django.contrib.auth import get_user_model
    
    # Get statistics (shown to everyone)
    stats = {
        'total_projects': Project.objects.count(),
        'total_topics': Topic.objects.count(),
        'total_events': Event.objects.count(),
        'total_resources': Resource.objects.count(),
    }
    
    context = {
        'stats': stats,
    }
    
    # Only show detailed content for authenticated users
    if request.user.is_authenticated:
        # Get recent content for homepage
        recent_projects = Project.objects.select_related('creator').order_by('-created_at')[:6]
        recent_topics = Topic.objects.select_related('author', 'category').annotate(
            post_count=Count('posts')
        ).order_by('-created_at')[:6]
        upcoming_events = Event.objects.filter(start_date__gte=timezone.now()).order_by('start_date')[:6]
        featured_resources = Resource.objects.filter(is_featured=True).select_related('author', 'category')[:6]
        
        # Get user stats
        User = get_user_model()
        try:
            user = request.user
            user_stats = {
                'projects_created': user.created_projects.count(),
                'projects_joined': user.joined_projects.count(),
                'topics_started': Topic.objects.filter(author=user).count(),
            }
            context['user_stats'] = user_stats
        except:
            pass
        
        context.update({
            'recent_projects': recent_projects,
            'recent_topics': recent_topics,
            'upcoming_events': upcoming_events,
            'featured_resources': featured_resources,
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
    model = Topic
    template_name = 'forums/topics.html'
    context_object_name = 'topics'
    paginate_by = 20

    def get_queryset(self):
        queryset = Topic.objects.annotate(
            post_count=Count('posts')
        ).select_related('author', 'category')

        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        # Sort by last updated topic
        return queryset.order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category')
        context['search_query'] = self.request.GET.get('search', '')
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
# Post Create View
# -------------------------
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
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


# -------------------------
# Post Update View
# -------------------------
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'forums/post_form.html'
    fields = ['content']

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def form_valid(self, form):
        form.instance.is_edited = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.topic.pk})


# -------------------------
# Post Delete View
# -------------------------
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'forums/post_confirm_delete.html'

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('forums:topic_detail', kwargs={'pk': self.object.topic.pk})


# -------------------------
# Topic Like Functionality
# -------------------------
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
