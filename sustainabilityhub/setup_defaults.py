"""
One-time script to create default categories for forums and resources.
Run this after creating your superuser account.
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sustainabilityhub.settings')
django.setup()

from forums.models import Category
from resources.models import ResourceCategory


def create_default_forum_categories():
    """Create default forum categories"""
    default_categories = [
        {
            'name': 'General Discussion',
            'description': 'General discussions about sustainability, environmental topics, and community news.'
        },
        {
            'name': 'Projects & Collaborations',
            'description': 'Share your sustainability projects, find collaborators, and discuss project ideas.'
        },
        {
            'name': 'Resources & Tools',
            'description': 'Share resources, tools, guides, and helpful information for sustainable living.'
        },
    ]
    
    created_count = 0
    for cat_data in default_categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            created_count += 1
            print(f'✓ Created forum category: {category.name}')
        else:
            print(f'- Forum category already exists: {category.name}')
    
    return created_count


def create_default_resource_categories():
    """Create default resource categories"""
    default_categories = [
        {
            'name': 'Articles & Guides',
            'description': 'Educational articles, guides, and how-to resources for sustainable living.'
        },
        {
            'name': 'Tools & Apps',
            'description': 'Software tools, mobile apps, and digital resources for sustainability.'
        },
        {
            'name': 'Research & Studies',
            'description': 'Scientific research, studies, and reports on environmental topics.'
        },
    ]
    
    created_count = 0
    for cat_data in default_categories:
        category, created = ResourceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            created_count += 1
            print(f'✓ Created resource category: {category.name}')
        else:
            print(f'- Resource category already exists: {category.name}')
    
    return created_count


if __name__ == '__main__':
    print('Creating default categories...\n')
    
    forum_count = create_default_forum_categories()
    print()
    resource_count = create_default_resource_categories()
    
    print(f'\n✅ Setup complete!')
    print(f'   - Created {forum_count} forum categories')
    print(f'   - Created {resource_count} resource categories')

