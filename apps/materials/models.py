from django.db import models
from django.conf import settings
import uuid


class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone_primary = models.CharField(max_length=30)
    phone_secondary = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suppliers'
        ordering = ['name']

    def __str__(self):
        return self.name


class MaterialCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'material_categories'
        verbose_name_plural = 'Material Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Material(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(MaterialCategory, on_delete=models.SET_NULL, null=True, related_name='materials')
    unit = models.CharField(max_length=50, help_text='e.g. 50kg bag, per length, per tipper')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'materials'
        ordering = ['category__name', 'name']

    def __str__(self):
        return f'{self.name} ({self.unit})'

    @property
    def current_price(self):
        return self.prices.filter(is_active=True).order_by('-effective_date').first()


class MaterialPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='prices')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'material_prices'
        ordering = ['-effective_date']

    def __str__(self):
        return f'{self.material.name} - {self.supplier.name}: {self.currency} {self.price}'


class CostAnomalyFlag(models.Model):
    OPEN = 'open'
    REVIEWED = 'reviewed'
    DISMISSED = 'dismissed'

    STATUS_CHOICES = [
        (OPEN, 'Open'),
        (REVIEWED, 'Reviewed'),
        (DISMISSED, 'Dismissed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stage = models.ForeignKey('stages.Stage', on_delete=models.CASCADE, related_name='anomaly_flags')
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    submitted_price = models.DecimalField(max_digits=12, decimal_places=2)
    database_price = models.DecimalField(max_digits=12, decimal_places=2)
    variance_percent = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cost_anomaly_flags'
        ordering = ['-created_at']

    def __str__(self):
        return f'Anomaly: {self.material.name} - {self.variance_percent}% variance'
