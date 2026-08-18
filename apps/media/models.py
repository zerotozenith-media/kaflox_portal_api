from django.db import models
from django.conf import settings
import uuid


class ProjectMedia(models.Model):
    PHOTO    = 'photo'
    VIDEO    = 'video'
    DELIVERY = 'delivery'

    TYPE_CHOICES = [
        (PHOTO,    'Photo'),
        (VIDEO,    'Video'),
        (DELIVERY, 'Delivery Footage'),
    ]

    HOT     = 'hot'
    COOL    = 'cool'
    ARCHIVE = 'archive'
    DELETED = 'deleted'

    TIER_CHOICES = [
        (HOT,     'Hot'),
        (COOL,    'Cool'),
        (ARCHIVE, 'Archive'),
        (DELETED, 'Deleted'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project     = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='media')
    stage       = models.ForeignKey(
        'stages.Stage', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='media'
    )
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    media_type  = models.CharField(max_length=10, choices=TYPE_CHOICES, default=PHOTO)
    title       = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    # Azure Blob Storage
    file             = models.FileField(upload_to='project-media/')
    blob_name        = models.CharField(max_length=500, blank=True)
    blob_url         = models.URLField(blank=True)
    file_size        = models.PositiveBigIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True, help_text='Video duration')

    # Storage tier lifecycle
    storage_tier             = models.CharField(max_length=10, choices=TIER_CHOICES, default=HOT)
    tier_updated_at          = models.DateTimeField(null=True, blank=True)
    deletion_scheduled_at    = models.DateTimeField(null=True, blank=True)
    client_notified_deletion = models.BooleanField(default=False)

    # Delivery matching
    delivery_log = models.ForeignKey(
        'staff.DeliveryLog', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='footage'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_media'
        ordering = ['-created_at']
        verbose_name = 'Project Media'
        verbose_name_plural = 'Project Media'

    def __str__(self):
        return f'{self.get_media_type_display()} - {self.project.name} ({self.created_at.date()})'


class ProjectDocument(models.Model):
    """Legal and project documents uploaded by admin, downloadable by the client."""
    CONTRACT = 'contract'
    LEGAL    = 'legal'
    DRAWING  = 'drawing'
    PERMIT   = 'permit'
    SIGNOFF  = 'signoff'
    REPORT   = 'report'
    POLICY   = 'policy'
    OTHER    = 'other'

    TYPE_CHOICES = [
        (CONTRACT, 'Contract'),
        (LEGAL,    'Legal'),
        (DRAWING,  'Drawing'),
        (PERMIT,   'Permit'),
        (SIGNOFF,  'Sign-Off'),
        (REPORT,   'Report'),
        (POLICY,   'Policy'),
        (OTHER,    'Other'),
    ]

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project       = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='documents')
    uploaded_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    name          = models.CharField(max_length=200, help_text='Display name of the document')
    document_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=OTHER)
    description   = models.TextField(blank=True)

    # Azure Blob Storage (documents container)
    file      = models.FileField(upload_to='project-documents/')
    blob_name = models.CharField(max_length=500, blank=True)
    blob_url  = models.URLField(blank=True)
    file_size = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_documents'
        ordering = ['document_type', '-created_at']
        verbose_name = 'Project Document'
        verbose_name_plural = 'Project Documents'

    def __str__(self):
        return f'{self.name} ({self.get_document_type_display()}) - {self.project.name}'
