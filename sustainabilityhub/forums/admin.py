from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Topic, Post, TopicPost, TopicLike, PostReaction, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'topic_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    
    def topic_count(self, obj):
        count = obj.topics.count()
        return format_html('<span style="color: var(--accent-2); font-weight: bold;">{}</span>', count)
    topic_count.short_description = 'Topics'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'post_type', 'preview', 'category', 'created_at']
    search_fields = ['content', 'author__username']
    list_filter = ['post_type', 'category', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def preview(self, obj):
        preview_text = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return format_html('<span style="color: var(--muted);">{}</span>', preview_text)
    preview.short_description = 'Content Preview'


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'reaction_type', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'author', 'preview', 'parent', 'created_at']
    search_fields = ['content', 'author__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def preview(self, obj):
        preview_text = obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
        return format_html('<span style="color: var(--muted);">{}</span>', preview_text)
    preview.short_description = 'Content Preview'


# Legacy admin classes
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'post_count', 'views', 'is_pinned', 'is_locked', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    list_filter = ['category', 'is_pinned', 'is_locked', 'created_at']
    readonly_fields = ['created_at', 'updated_at', 'views']
    
    def post_count(self, obj):
        count = obj.posts.count()
        return format_html('<span style="color: var(--accent-2); font-weight: bold;">{}</span>', count)
    post_count.short_description = 'Posts'


@admin.register(TopicPost)
class TopicPostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'author', 'preview', 'is_edited', 'created_at']
    search_fields = ['content', 'author__username', 'topic__title']
    list_filter = ['created_at', 'is_edited']
    readonly_fields = ['created_at', 'updated_at']
    
    def preview(self, obj):
        preview_text = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return format_html('<span style="color: var(--muted);">{}</span>', preview_text)
    preview.short_description = 'Content Preview'


@admin.register(TopicLike)
class TopicLikeAdmin(admin.ModelAdmin):
    list_display = ['topic', 'user', 'created_at']
    search_fields = ['topic__title', 'user__username']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
