from django.core.management.base import BaseCommand
from resources.models import ResourceCategory


class Command(BaseCommand):
    help = 'Creates default resource categories'

    def handle(self, *args, **options):
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
            {
                'name': 'Videos & Media',
                'description': 'Video tutorials, documentaries, and multimedia content about sustainability.'
            },
            {
                'name': 'Organizations & Networks',
                'description': 'Links to sustainability organizations, networks, and communities.'
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
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'[-] Category already exists: {category.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} categories created. Total categories: {ResourceCategory.objects.count()}')
        )

