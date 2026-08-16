from rest_framework import serializers
from .models import StaffRole, StaffMember, AttendanceRecord, MaterialIssuance, DeliveryLog


class StaffRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffRole
        fields = ['id', 'name', 'description', 'is_active', 'order']


class StaffMemberSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = StaffMember
        fields = ['id', 'staff_id', 'first_name', 'last_name', 'full_name', 'phone', 'role', 'role_name', 'staff_type', 'status', 'company_name', 'company_registration']

    def get_role_name(self, obj):
        return obj.role.name if obj.role else None


class AttendanceSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'staff_member', 'staff_name', 'project', 'date', 'status', 'time_in', 'task_assigned', 'logged_by', 'created_at']
        read_only_fields = ['id', 'logged_by', 'created_at']

    def get_staff_name(self, obj):
        return obj.staff_member.full_name


class MaterialIssuanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialIssuance
        fields = ['id', 'project', 'stage', 'issued_to', 'material', 'quantity', 'purpose', 'issued_by', 'date', 'issued_at']
        read_only_fields = ['id', 'issued_by', 'issued_at']


class DeliveryLogSerializer(serializers.ModelSerializer):
    supplier_name = serializers.SerializerMethodField()
    material_name = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryLog
        fields = ['id', 'project', 'stage', 'supplier', 'supplier_name', 'material', 'material_name', 'quantity', 'unit_price', 'total_amount', 'delivery_date', 'delivery_time', 'receipt_photo', 'status', 'supervisor_confirmed', 'client_confirmed', 'camera_footage_ref', 'created_at']
        read_only_fields = ['id', 'logged_by', 'created_at']

    def get_supplier_name(self, obj): return obj.supplier.name if obj.supplier else None
    def get_material_name(self, obj): return obj.material.name
