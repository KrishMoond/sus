"""
Test script to verify login functionality
Run: python test_login.py
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainabilityhub.settings')
django.setup()

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import make_password

User = get_user_model()

print("=" * 60)
print("LOGIN SYSTEM DIAGNOSTIC")
print("=" * 60)
print()

# List all users
users = User.objects.all()
print(f"Total users in database: {users.count()}")
print()

if users.count() > 0:
    print("Available users:")
    for user in users:
        print(f"  - Username: {user.username}")
        print(f"    Email: {user.email or 'No email'}")
        print(f"    Active: {user.is_active}")
        print(f"    Staff: {user.is_staff}")
        print(f"    Superuser: {user.is_superuser}")
        print()
    
    # Test authentication with a known password
    test_user = users.first()
    print(f"Testing authentication for: {test_user.username}")
    print()
    
    # Try to authenticate with empty password
    result = authenticate(username=test_user.username, password='')
    print(f"Authenticate with empty password: {result}")
    
    # Try to authenticate with 'password' (common default)
    result = authenticate(username=test_user.username, password='password')
    print(f"Authenticate with 'password': {result}")
    
    # Try to authenticate with username as password
    result = authenticate(username=test_user.username, password=test_user.username)
    print(f"Authenticate with username as password: {result}")
    
    print()
    print("=" * 60)
    print("NOTE: Passwords are hashed, so we can't check the actual password.")
    print("If authentication fails, you may need to:")
    print("  1. Reset the password via Django admin")
    print("  2. Or create a new user account")
    print("=" * 60)
else:
    print("No users found in database.")
    print("Create a user by running: python manage.py createsuperuser")
    print("Or register a new account at: /accounts/register/")

