from django.db import models
from django.conf import settings
import uuid


class Project(models.Model):
    RESIDENTIAL = 'residential'
    COMMERCIAL = 'commercial'
    MIXED_USE = 'mixed_use'
    RENOVATION = 'renovation'

    TYPE_CHOICES = [
        (RESIDENTIAL, 'Residential'),
        (COMMERCIAL, 'Commercial'),
        (MIXED_USE, 'Mixed Use'),
        (RENOVATION, 'Renovation'),
    ]

    ACTIVE = 'active'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (ON_HOLD, 'On Hold'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='projects', limit_choices_to={'role': 'client'}
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=RESIDENTIAL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)

    # Location
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')

    # Financials
    contract_value = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    management_fee_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=settings.KAFLOX_MANAGEMENT_FEE_PERCENT
    )

    # Timeline
    start_date = models.DateField(null=True, blank=True)
    estimated_end_date = models.DateField(null=True, blank=True)
    actual_end_date = models.DateField(null=True, blank=True)

    # Camera
    camera_stream_url = models.URLField(blank=True, help_text='Azure Media Services stream URL')
    camera_online = models.BooleanField(default=False)

    # Assigned team
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_projects',
        blank=True,
        limit_choices_to={'role': 'team_member'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.client.full_name})'

    @property
    def total_stages(self):
        return self.stages.count()

    @property
    def completed_stages(self):
        return self.stages.filter(status='completed').count()

    @property
    def progress_percent(self):
        total = self.total_stages
        if total == 0:
            return 0
        return round((self.completed_stages / total) * 100)

    @property
    def total_paid(self):
        from apps.payments.models import Payment
        from django.db.models import Sum
        result = Payment.objects.filter(
            project=self, status=Payment.CONFIRMED
        ).aggregate(total=Sum('amount'))
        return result['total'] or 0


class EOISubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    project_type = models.CharField(max_length=20)
    project_location = models.CharField(max_length=200)
    budget_range = models.CharField(max_length=50)
    timeline = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    tc_accepted = models.BooleanField(default=False)

    # Status
    PENDING = 'pending'
    CONTACTED = 'contacted'
    CONVERTED = 'converted'
    DECLINED = 'declined'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONTACTED, 'Contacted'),
        (CONVERTED, 'Converted to Client'),
        (DECLINED, 'Declined'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    showcase_user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='eoi'
    )
    notes = models.TextField(blank=True, help_text='Internal admin notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'eoi_submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f'EOI: {self.first_name} {self.last_name} ({self.email})'
