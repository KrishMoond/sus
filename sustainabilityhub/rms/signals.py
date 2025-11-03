from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Report
from notifications.utils import create_notification

User = get_user_model()

@receiver(post_save, sender=Report)
def report_notification(sender, instance, created, **kwargs):
    if created:
        # Notify all superusers about new report
        superusers = User.objects.filter(is_superuser=True)
        for admin in superusers:
            create_notification(
                recipient=admin,
                notification_type='report_created',
                title='New Report Submitted',
                message=f'New {instance.get_category_display()} report: {instance.subject}',
                url=f'/reports/admin/'
            )
    elif instance.status in ['resolved', 'rejected'] and instance.admin_response:
        # Notify reporter about resolution
        create_notification(
            recipient=instance.reporter,
            notification_type='report_resolved',
            title='Report Updated',
            message=f'Your report "{instance.subject}" has been {instance.get_status_display().lower()}',
            url=f'/reports/my-reports/'
        )