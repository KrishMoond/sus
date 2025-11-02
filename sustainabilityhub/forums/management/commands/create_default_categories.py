from django.core.management.base import BaseCommand
from forums.models import Category


class Command(BaseCommand):
    help = 'Creates default forum categories'

    def handle(self, *args, **options):
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
            {
                'name': 'Events & Meetups',
                'description': 'Discuss upcoming events, share event experiences, and organize meetups.'
            },
            {
                'name': 'Q&A',
                'description': 'Ask questions and get answers from the community about sustainability topics.'
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
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'[-] Category already exists: {category.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} categories created. Total categories: {Category.objects.count()}')
        )

