from django.db import models
from django.conf import settings
import uuid


class Payment(models.Model):
    PENDING = 'pending'
    PROCESSING = 'processing'
    CONFIRMED = 'confirmed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (CONFIRMED, 'Confirmed'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]

    CARD = 'card'
    BANK_TRANSFER = 'bank_transfer'
    FLUTTERWAVE = 'flutterwave'

    METHOD_CHOICES = [
        (CARD, 'Card'),
        (BANK_TRANSFER, 'Bank Transfer'),
        (FLUTTERWAVE, 'Flutterwave'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, related_name='payments')
    stage = models.OneToOneField(
        'stages.Stage', on_delete=models.PROTECT,
        related_name='payment', null=True, blank=True
    )
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments')

    # Amounts
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    material_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    labour_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    management_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    management_fee_percent = models.DecimalField(max_digits=5, decimal_places=2, default=15)

    # Gateway
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, blank=True)
    flutterwave_ref = models.CharField(max_length=200, blank=True, db_index=True)
    flutterwave_tx_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)

    # Reminders
    reminder_sent_count = models.PositiveIntegerField(default=0)
    last_reminder_sent_at = models.DateTimeField(null=True, blank=True)

    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f'Payment {self.id} - {self.project.name} - {self.currency} {self.amount} ({self.status})'


class RefundRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    PROCESSED = 'processed'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (PROCESSED, 'Processed'),
        (REJECTED, 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT, related_name='refund_requests')
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    reason = models.TextField()
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2)
    deduction_effort = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    deduction_processing = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    net_refund = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    admin_notes = models.TextField(blank=True)
    processing_deadline = models.DateField(null=True, blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'refund_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'Refund: {self.project.name} - {self.status}'
