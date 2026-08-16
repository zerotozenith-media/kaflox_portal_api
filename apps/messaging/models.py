from django.db import models
from django.conf import settings
import uuid


class MessageThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE, related_name='threads'
    )
    subject = models.CharField(max_length=200, blank=True)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='threads', blank=True
    )
    # Agents: staff members assigned to handle messaging for this thread
    agents = models.ManyToManyField(
        'staff.StaffMember',
        related_name='assigned_threads',
        blank=True,
        help_text='Staff members assigned to respond to client messages in this thread'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'message_threads'
        ordering = ['-updated_at']

    def __str__(self):
        return f'Thread: {self.project.name} - {self.subject or "General"}'

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(
        MessageThread, on_delete=models.CASCADE, related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages'
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    attachment = models.FileField(upload_to='message-attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.full_name} in {self.thread}'


class Notification(models.Model):
    # Types
    PAYMENT_DUE       = 'payment_due'
    PAYMENT_CONFIRMED = 'payment_confirmed'
    STAGE_COMPLETE    = 'stage_complete'
    STAGE_STARTED     = 'stage_started'
    MESSAGE_RECEIVED  = 'message_received'
    MEDIA_UPLOADED    = 'media_uploaded'
    MEDIA_EXPIRING    = 'media_expiring'
    INSPECTION_WINDOW = 'inspection_window'

    TYPE_CHOICES = [
        (PAYMENT_DUE,       'Payment Due'),
        (PAYMENT_CONFIRMED, 'Payment Confirmed'),
        (STAGE_COMPLETE,    'Stage Complete'),
        (STAGE_STARTED,     'Stage Started'),
        (MESSAGE_RECEIVED,  'Message Received'),
        (MEDIA_UPLOADED,    'Media Uploaded'),
        (MEDIA_EXPIRING,    'Media Expiring'),
        (INSPECTION_WINDOW, 'Inspection Window Open'),
    ]

    # Channels
    IN_APP    = 'in_app'
    EMAIL     = 'email'
    WHATSAPP  = 'whatsapp'    # Future: WhatsApp integration hook

    CHANNEL_CHOICES = [
        (IN_APP,   'In-App'),
        (EMAIL,    'Email'),
        (WHATSAPP, 'WhatsApp'),
    ]

    # Status
    PENDING = 'pending'
    SENT    = 'sent'
    FAILED  = 'failed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SENT,    'Sent'),
        (FAILED,  'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    project = models.ForeignKey(
        'projects.Project', on_delete=models.CASCADE,
        related_name='notifications', null=True, blank=True
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    body = models.TextField()
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default=IN_APP)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.recipient.full_name}: {self.title}'
