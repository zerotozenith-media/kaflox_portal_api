"""
Celery tasks: notifications, payment reminders, media archiving.
"""
import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger('kaflox')


@shared_task
def send_email_notification(recipient_email, subject, body):
    """Send email via Azure Communication Services."""
    try:
        from azure.communication.email import EmailClient
        client = EmailClient.from_connection_string(settings.AZURE_COMM_CONNECTION_STRING)
        message = {
            "senderAddress": settings.AZURE_COMM_SENDER_EMAIL,
            "recipients": {"to": [{"address": recipient_email}]},
            "content": {"subject": subject, "plainText": body},
        }
        poller = client.begin_send(message)
        result = poller.result()
        logger.info(f'Email sent to {recipient_email}: {result}')
    except Exception as e:
        logger.error(f'Failed to send email to {recipient_email}: {e}')


@shared_task
def send_sms_notification(recipient_phone, message):
    """Send SMS via Azure Communication Services."""
    try:
        from azure.communication.sms import SmsClient
        client = SmsClient.from_connection_string(settings.AZURE_COMM_CONNECTION_STRING)
        response = client.send(
            from_=settings.AZURE_COMM_SENDER_PHONE,
            to=[recipient_phone],
            message=message,
        )
        logger.info(f'SMS sent to {recipient_phone}: {response}')
    except Exception as e:
        logger.error(f'Failed to send SMS to {recipient_phone}: {e}')


@shared_task
def check_payment_reminders():
    """Check for overdue stage payments and send reminders."""
    from apps.payments.models import Payment
    from apps.projects.models import Project

    now = timezone.now()
    reminder_days = settings.KAFLOX_PAYMENT_REMINDER_DAYS

    pending_payments = Payment.objects.filter(status=Payment.PENDING).select_related('project__client', 'stage')

    for payment in pending_payments:
        client = payment.project.client
        days_pending = (now.date() - payment.created_at.date()).days

        if days_pending in reminder_days:
            subject = f'Payment Reminder: {payment.project.name}'
            body = (
                f'Dear {client.first_name},\n\n'
                f'This is a reminder that your stage payment of '
                f'{payment.currency} {payment.amount:,.2f} for '
                f'{payment.stage.name if payment.stage else "your project"} is pending.\n\n'
                f'Please log in to your portal to complete payment: '
                f'https://portal.kafloxengineering.com\n\n'
                f'Kaflox Engineering Services Limited'
            )
            send_email_notification.delay(client.email, subject, body)
            payment.reminder_sent_count += 1
            payment.last_reminder_sent_at = now
            payment.save(update_fields=['reminder_sent_count', 'last_reminder_sent_at'])
            logger.info(f'Payment reminder sent to {client.email} for payment {payment.id}')


@shared_task
def check_inspection_windows():
    """Auto-accept stages where inspection window has passed without objection."""
    from apps.stages.models import Stage
    from apps.messaging.models import Notification

    now = timezone.now()
    expired = Stage.objects.filter(
        status=Stage.INSPECTION,
        inspection_deadline__lt=now,
        client_accepted=False,
    )

    for stage in expired:
        stage.client_accepted = True
        stage.client_accepted_at = now
        stage.status = Stage.COMPLETED
        stage.actual_end = now.date()
        stage.save()

        Notification.objects.create(
            recipient=stage.project.client,
            project=stage.project,
            notification_type=Notification.STAGE_UPDATE,
            title=f'Stage Accepted: {stage.name}',
            body=(
                f'The 14-day inspection window for {stage.name} has passed without objection. '
                f'The stage has been automatically accepted per your contract terms.'
            ),
        )
        logger.info(f'Auto-accepted stage {stage.id} for project {stage.project.name}')


@shared_task
def archive_completed_stage_media():
    """Move media to Cool storage tier 30 days after stage completion."""
    from apps.media.models import ProjectMedia
    from apps.stages.models import Stage

    cutoff = timezone.now() - timedelta(days=settings.KAFLOX_MEDIA_COOL_DAYS)
    completed_stages = Stage.objects.filter(
        status=Stage.COMPLETED,
        actual_end__lte=cutoff.date(),
    )

    for stage in completed_stages:
        media_to_cool = stage.media.filter(storage_tier=ProjectMedia.HOT)
        count = media_to_cool.count()
        if count:
            media_to_cool.update(storage_tier=ProjectMedia.COOL, tier_updated_at=timezone.now())
            logger.info(f'Moved {count} media items to Cool for stage {stage.name}')


@shared_task
def schedule_project_media_deletion():
    """Schedule media deletion 90 days after project handover."""
    from apps.media.models import ProjectMedia
    from apps.projects.models import Project
    from apps.messaging.models import Notification

    cutoff = timezone.now() - timedelta(days=settings.KAFLOX_MEDIA_DELETE_DAYS)
    handed_over = Project.objects.filter(
        status=Project.COMPLETED,
        actual_end_date__lte=cutoff.date(),
    )

    for project in handed_over:
        media_to_delete = project.media.filter(
            storage_tier__in=[ProjectMedia.COOL, ProjectMedia.HOT],
            client_notified_deletion=False,
        )
        if media_to_delete.exists():
            deletion_date = timezone.now() + timedelta(days=settings.KAFLOX_MEDIA_DELETE_DAYS)
            media_to_delete.update(
                deletion_scheduled_at=deletion_date,
                client_notified_deletion=True,
            )
            Notification.objects.create(
                recipient=project.client,
                project=project,
                notification_type=Notification.GENERAL,
                title='Project Media Scheduled for Deletion',
                body=(
                    f'Your project media for {project.name} will be permanently deleted in 90 days '
                    f'per your signed media retention policy. Please download any media you wish to keep '
                    f'from your portal before {deletion_date.strftime("%d %B %Y")}.'
                ),
            )
            logger.info(f'Notified client {project.client.email} of media deletion for {project.name}')
