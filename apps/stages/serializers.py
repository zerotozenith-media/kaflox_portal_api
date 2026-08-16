from rest_framework import serializers
from .models import Stage, StageTemplate, StageComment, SnagItem


class StageTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageTemplate
        fields = ['id', 'name', 'description', 'project_type', 'default_order', 'is_active']


class StageCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = StageComment
        fields = ['id', 'stage', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']

    def get_author_name(self, obj):
        return obj.author.full_name


class SnagItemSerializer(serializers.ModelSerializer):
    raised_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SnagItem
        fields = [
            'id', 'stage', 'raised_by', 'raised_by_name',
            'title', 'description', 'status', 'resolved_at', 'created_at'
        ]
        read_only_fields = ['id', 'raised_by', 'created_at']

    def get_raised_by_name(self, obj):
        return obj.raised_by.full_name


class AssignedStaffSerializer(serializers.Serializer):
    """Minimal read-only serializer for staff assigned to a stage."""
    id        = serializers.UUIDField()
    staff_id  = serializers.CharField()
    full_name = serializers.CharField()
    role_name = serializers.SerializerMethodField()

    def get_role_name(self, obj):
        return obj.role.name if obj.role else None


class StageSerializer(serializers.ModelSerializer):
    management_fee   = serializers.ReadOnlyField()
    total_amount_due = serializers.ReadOnlyField()
    comments         = StageCommentSerializer(many=True, read_only=True)
    snag_items       = SnagItemSerializer(many=True, read_only=True)
    assigned_staff   = AssignedStaffSerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = [
            'id', 'project', 'template', 'name', 'description', 'order', 'status',
            'assigned_staff',
            'estimated_cost', 'material_cost', 'labour_cost',
            'management_fee', 'total_amount_due',
            'planned_start', 'planned_end', 'actual_start', 'actual_end',
            'inspection_started_at', 'inspection_deadline',
            'client_accepted', 'client_accepted_at',
            'admin_notes', 'client_notes',
            'comments', 'snag_items',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'management_fee', 'total_amount_due'
        ]
