"""
Utility to reset a user's password.
Usage: python reset_user_password.py <username> <new_password>
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainabilityhub.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if len(sys.argv) < 3:
    print("Usage: python reset_user_password.py <username> <new_password>")
    print()
    print("Available users:")
    for user in User.objects.all():
        print(f"  - {user.username}")
    sys.exit(1)

username = sys.argv[1]
new_password = sys.argv[2]

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    print(f"✓ Password reset successfully for user: {username}")
    print(f"  You can now login with:")
    print(f"    Username: {username}")
    print(f"    Password: {new_password}")
except User.DoesNotExist:
    print(f"✗ User '{username}' not found.")
    print("\nAvailable users:")
    for u in User.objects.all():
        print(f"  - {u.username}")

