from django.db import models
from django.conf import settings
import uuid


class StageTemplate(models.Model):
    RESIDENTIAL = 'residential'
    COMMERCIAL  = 'commercial'
    BOTH        = 'both'

    TYPE_CHOICES = [
        (RESIDENTIAL, 'Residential'),
        (COMMERCIAL,  'Commercial'),
        (BOTH,        'Both'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name         = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    project_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=BOTH)
    default_order = models.PositiveIntegerField(default=0)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'stage_templates'
        ordering = ['default_order']

    def __str__(self):
        return self.name


class Stage(models.Model):
    PENDING          = 'pending'
    AWAITING_PAYMENT = 'awaiting_payment'
    IN_PROGRESS      = 'in_progress'
    INSPECTION       = 'inspection'
    COMPLETED        = 'completed'

    STATUS_CHOICES = [
        (PENDING,          'Pending'),
        (AWAITING_PAYMENT, 'Awaiting Payment'),
        (IN_PROGRESS,      'In Progress'),
        (INSPECTION,       'In Inspection Window'),
        (COMPLETED,        'Completed'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project     = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='stages')
    template    = models.ForeignKey(StageTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    name        = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order       = models.PositiveIntegerField(default=0)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)

    # Staff assignment -- multiple staff can be assigned to a stage
    assigned_staff = models.ManyToManyField(
        'staff.StaffMember',
        related_name='assigned_stages',
        blank=True,
        help_text='Staff members assigned to work on this stage'
    )

    # Financials
    estimated_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    material_cost  = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    labour_cost    = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    # Timeline
    planned_start = models.DateField(null=True, blank=True)
    planned_end   = models.DateField(null=True, blank=True)
    actual_start  = models.DateField(null=True, blank=True)
    actual_end    = models.DateField(null=True, blank=True)

    # Inspection window
    inspection_started_at = models.DateTimeField(null=True, blank=True)
    inspection_deadline   = models.DateTimeField(null=True, blank=True)
    client_accepted       = models.BooleanField(default=False)
    client_accepted_at    = models.DateTimeField(null=True, blank=True)

    # Notes
    admin_notes  = models.TextField(blank=True)
    client_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stages'
        ordering = ['order']

    def __str__(self):
        return f'{self.project.name} - Stage {self.order}: {self.name}'

    @property
    def management_fee(self):
        total = self.material_cost + self.labour_cost
        return total * (self.project.management_fee_percent / 100)

    @property
    def total_amount_due(self):
        return self.material_cost + self.labour_cost + self.management_fee


class StageComment(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stage      = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='comments')
    author     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stage_comments'
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.full_name} on {self.stage.name}'


class SnagItem(models.Model):
    OPEN        = 'open'
    IN_PROGRESS = 'in_progress'
    RESOLVED    = 'resolved'
    ACCEPTED    = 'accepted'

    STATUS_CHOICES = [
        (OPEN,        'Open'),
        (IN_PROGRESS, 'In Progress'),
        (RESOLVED,    'Resolved'),
        (ACCEPTED,    'Accepted by Client'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stage       = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='snag_items')
    raised_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title       = models.CharField(max_length=200)
    description = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'snag_items'
        ordering = ['-created_at']

    def __str__(self):
        return f'Snag: {self.title} ({self.status})'
