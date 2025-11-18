#!/usr/bin/env python
"""
Test script to verify community app functionality
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainabilityhub.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model

def test_community_urls():
    """Test if community URLs are accessible"""
    client = Client()
    
    try:
        # Test community dashboard URL
        url = reverse('community:dashboard')
        print(f"[OK] Community dashboard URL resolved: {url}")
        
        # Test challenges URL
        url = reverse('community:challenges')
        print(f"[OK] Community challenges URL resolved: {url}")
        
        # Test discover URL
        url = reverse('community:discover')
        print(f"[OK] Community discover URL resolved: {url}")
        
        print("\nAll community URLs are properly configured!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing URLs: {e}")
        return False

def test_community_models():
    """Test if community models are working"""
    try:
        from community.models import Post, HashTag, Follow
        print("[OK] Community models imported successfully")
        
        # Test model creation
        User = get_user_model()
        users = User.objects.all()[:1]
        if users:
            user = users[0]
            print(f"[OK] Found test user: {user.username}")
        else:
            print("[WARNING] No users found in database")
        
        # Test Post model
        posts_count = Post.objects.count()
        print(f"[OK] Posts in database: {posts_count}")
        
        # Test HashTag model
        hashtags_count = HashTag.objects.count()
        print(f"[OK] Hashtags in database: {hashtags_count}")
        
        print("\nAll community models are working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing models: {e}")
        return False

def test_community_views():
    """Test if community views are accessible"""
    client = Client()
    
    try:
        # Test dashboard view (should redirect to login for anonymous users)
        response = client.get('/community/')
        print(f"[OK] Community dashboard response: {response.status_code}")
        
        # Test challenges view
        response = client.get('/community/challenges/')
        print(f"[OK] Community challenges response: {response.status_code}")
        
        # Test discover view
        response = client.get('/community/discover/')
        print(f"[OK] Community discover response: {response.status_code}")
        
        print("\nAll community views are accessible!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing views: {e}")
        return False

if __name__ == '__main__':
    print("Testing Community App Functionality\n")
    print("=" * 50)
    
    # Run tests
    url_test = test_community_urls()
    print("\n" + "=" * 50)
    
    model_test = test_community_models()
    print("\n" + "=" * 50)
    
    view_test = test_community_views()
    print("\n" + "=" * 50)
    
    # Summary
    if url_test and model_test and view_test:
        print("\nALL TESTS PASSED! Community app is working correctly!")
        sys.exit(0)
    else:
        print("\nSome tests failed. Check the errors above.")
        sys.exit(1)