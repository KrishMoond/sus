from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, PostReaction, Comment, CommentReaction, Follow, HashTag

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar_url']
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None


class HashTagSerializer(serializers.ModelSerializer):
    post_count = serializers.ReadOnlyField()
    
    class Meta:
        model = HashTag
        fields = ['id', 'name', 'post_count']


class CommentReactionSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = CommentReaction
        fields = ['id', 'user', 'reaction_type', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    reactions = CommentReactionSerializer(many=True, read_only=True)
    total_reactions = serializers.ReadOnlyField()
    replies = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'content', 'parent', 'created_at', 'updated_at',
            'is_edited', 'reactions', 'total_reactions', 'replies', 'user_reaction'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'is_edited']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []
    
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            return reaction.reaction_type if reaction else None
        return None


class PostReactionSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = PostReaction
        fields = ['id', 'user', 'reaction_type', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    reactions = PostReactionSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    hashtags = HashTagSerializer(many=True, read_only=True)
    total_reactions = serializers.ReadOnlyField()
    total_comments = serializers.ReadOnlyField()
    user_reaction = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    content_object_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'post_type', 'image', 'image_url',
            'link_url', 'link_title', 'created_at', 'updated_at', 'is_pinned',
            'is_featured', 'reactions', 'comments', 'hashtags', 'total_reactions',
            'total_comments', 'user_reaction', 'content_object_data'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            return reaction.reaction_type if reaction else None
        return None
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_content_object_data(self, obj):
        if obj.content_object:
            # Return basic info about linked object (project, event, etc.)
            return {
                'type': obj.content_type.model,
                'id': obj.object_id,
                'title': getattr(obj.content_object, 'title', str(obj.content_object))
            }
        return None


class PostCreateSerializer(serializers.ModelSerializer):
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Post
        fields = [
            'content', 'post_type', 'image', 'link_url', 'link_title', 'hashtags'
        ]
    
    def create(self, validated_data):
        hashtags_data = validated_data.pop('hashtags', [])
        post = Post.objects.create(**validated_data)
        
        # Handle hashtags
        for tag_name in hashtags_data:
            tag_name = tag_name.strip().lower().replace('#', '')
            if tag_name:
                hashtag, created = HashTag.objects.get_or_create(name=tag_name)
                post.hashtags.add(hashtag)
        
        return post


class FollowSerializer(serializers.ModelSerializer):
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'created_at']