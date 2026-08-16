from django.contrib import admin
from .models import StaffRole, StaffMember, AttendanceRecord, MaterialIssuance, DeliveryLog


@admin.register(StaffRole)
class StaffRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'order']
    list_editable = ['is_active', 'order']


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ['staff_id', 'full_name', 'role', 'staff_type', 'status', 'phone']
    list_filter = ['staff_type', 'status', 'role']
    search_fields = ['staff_id', 'first_name', 'last_name', 'phone']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['staff_member', 'project', 'date', 'status', 'time_in', 'task_assigned']
    list_filter = ['status', 'date']
    search_fields = ['staff_member__first_name', 'staff_member__last_name']
    date_hierarchy = 'date'


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ['material', 'supplier', 'project', 'quantity', 'delivery_date', 'status']
    list_filter = ['status', 'delivery_date']
    search_fields = ['material__name', 'supplier__name']
    date_hierarchy = 'delivery_date'
