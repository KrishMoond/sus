from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from .models import UserWarning
from .permissions import get_user_role

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'password', 'password_confirm', 'bio'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    avatar_url = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'bio', 'avatar', 'avatar_url', 'date_joined', 'last_login',
            'role', 'stats', 'is_following', 'followers_count', 'following_count'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None
    
    def get_role(self, obj):
        return get_user_role(obj)
    
    def get_stats(self, obj):
        return {
            'projects_created': obj.created_projects.count(),
            'projects_joined': obj.joined_projects.count(),
            'forum_posts': obj.forum_posts.count(),
            'community_posts': obj.community_posts.count(),
            'events_created': obj.created_events.count(),
        }
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return obj.followers.filter(follower=request.user).exists()
        return False
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested relationships"""
    avatar_url = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar_url', 'role']
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None
    
    def get_role(self, obj):
        return get_user_role(obj)


class UserWarningSerializer(serializers.ModelSerializer):
    """Serializer for user warnings"""
    issued_by = UserBasicSerializer(read_only=True)
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserWarning
        fields = [
            'id', 'user', 'issued_by', 'severity', 'reason', 'description',
            'created_at', 'is_active', 'viewed_at', 'justification',
            'justification_submitted_at'
        ]
        read_only_fields = ['id', 'created_at', 'viewed_at', 'justification_submitted_at']


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include username and password')


class UserSearchSerializer(serializers.ModelSerializer):
    """Serializer for user search results"""
    avatar_url = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'bio',
            'avatar_url', 'role', 'is_following'
        ]
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None
    
    def get_role(self, obj):
        return get_user_role(obj)
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return obj.followers.filter(follower=request.user).exists()
        return False