from django.db import models
from django.conf import settings
import uuid


class StaffRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'staff_roles'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class StaffMember(models.Model):
    DIRECT = 'direct'
    SUBCONTRACTOR = 'subcontractor'

    TYPE_CHOICES = [
        (DIRECT, 'Direct Employee'),
        (SUBCONTRACTOR, 'Subcontractor'),
    ]

    ACTIVE = 'active'
    INACTIVE = 'inactive'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_id = models.CharField(max_length=20, unique=True, help_text='e.g. KE-001')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30)
    role = models.ForeignKey(StaffRole, on_delete=models.SET_NULL, null=True)
    staff_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DIRECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)

    # Subcontractor fields
    company_name = models.CharField(max_length=200, blank=True)
    company_registration = models.CharField(max_length=100, blank=True)
    insurance_document = models.FileField(upload_to='staff-documents/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'staff_members'
        ordering = ['staff_id']

    def __str__(self):
        name = f'{self.first_name} {self.last_name}'
        if self.staff_type == self.SUBCONTRACTOR and self.company_name:
            name = f'{self.company_name} ({name})'
        return f'{self.staff_id} - {name}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class AttendanceRecord(models.Model):
    PRESENT = 'present'
    ABSENT = 'absent'
    HALF_DAY = 'half_day'

    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
        (HALF_DAY, 'Half Day'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='attendance')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PRESENT)
    time_in = models.TimeField(null=True, blank=True)
    task_assigned = models.CharField(max_length=300, blank=True)
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='attendance_logged'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance_records'
        ordering = ['-date']
        unique_together = ['staff_member', 'project', 'date']

    def __str__(self):
        return f'{self.staff_member} - {self.date} ({self.status})'


class MaterialIssuance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='material_issuances')
    stage = models.ForeignKey('stages.Stage', on_delete=models.SET_NULL, null=True, blank=True)
    issued_to = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='material_issuances')
    material = models.ForeignKey('materials.Material', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=300)
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='material_issuances_made'
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    date = models.DateField()

    class Meta:
        db_table = 'material_issuances'
        ordering = ['-date']

    def __str__(self):
        return f'{self.material.name} x{self.quantity} to {self.issued_to} on {self.date}'


class DeliveryLog(models.Model):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    DISPUTED = 'disputed'

    STATUS_CHOICES = [
        (PENDING, 'Pending Confirmation'),
        (CONFIRMED, 'Confirmed'),
        (DISPUTED, 'Disputed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='deliveries')
    stage = models.ForeignKey('stages.Stage', on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey('materials.Supplier', on_delete=models.SET_NULL, null=True)
    material = models.ForeignKey('materials.Material', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    delivery_date = models.DateField()
    delivery_time = models.TimeField(null=True, blank=True)
    receipt_photo = models.ImageField(upload_to='delivery-receipts/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    supervisor_confirmed = models.BooleanField(default=False)
    client_confirmed = models.BooleanField(default=False)
    camera_footage_ref = models.CharField(max_length=200, blank=True, help_text='Reference to camera footage timestamp')
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='deliveries_logged'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_logs'
        ordering = ['-delivery_date']

    def __str__(self):
        return f'Delivery: {self.material.name} x{self.quantity} on {self.delivery_date}'
