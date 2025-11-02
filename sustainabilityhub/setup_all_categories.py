"""
Quick script to create all default categories for both Forums and Resources.
Run this after creating your superuser account.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainabilityhub.settings')
django.setup()

from forums.models import Category
from resources.models import ResourceCategory


def create_forum_categories():
    """Create default forum categories"""
    categories = [
        {'name': 'General Discussion', 'description': 'General discussions about sustainability and environmental topics.'},
        {'name': 'Projects & Collaborations', 'description': 'Share projects and find collaborators.'},
        {'name': 'Resources & Tools', 'description': 'Share tools and helpful information.'},
    ]
    
    created = 0
    for cat_data in categories:
        cat, new = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if new:
            created += 1
            print(f'[OK] Created forum category: {cat.name}')
        else:
            print(f'[-] Forum category exists: {cat.name}')
    
    return created


def create_resource_categories():
    """Create default resource categories"""
    categories = [
        {'name': 'Articles & Guides', 'description': 'Educational articles and guides.'},
        {'name': 'Tools & Apps', 'description': 'Software tools and applications.'},
        {'name': 'Research & Studies', 'description': 'Scientific research and studies.'},
    ]
    
    created = 0
    for cat_data in categories:
        cat, new = ResourceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if new:
            created += 1
            print(f'[OK] Created resource category: {cat.name}')
        else:
            print(f'[-] Resource category exists: {cat.name}')
    
    return created


if __name__ == '__main__':
    print('=' * 50)
    print('Creating Default Categories')
    print('=' * 50)
    print()
    
    print('Creating Forum Categories...')
    forum_count = create_forum_categories()
    print()
    
    print('Creating Resource Categories...')
    resource_count = create_resource_categories()
    print()
    
    print('=' * 50)
    print('Summary:')
    print(f'  Forum categories: {Category.objects.count()} total ({forum_count} new)')
    print(f'  Resource categories: {ResourceCategory.objects.count()} total ({resource_count} new)')
    print('=' * 50)
    print()
    print('Done! Categories are now available in Forums and Resources sections.')

