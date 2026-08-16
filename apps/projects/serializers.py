from rest_framework import serializers
from .models import Project, EOISubmission
from apps.users.serializers import UserSerializer


class ProjectSerializer(serializers.ModelSerializer):
    client_name      = serializers.SerializerMethodField()
    progress_percent = serializers.ReadOnlyField()
    total_paid       = serializers.ReadOnlyField()
    total_stages     = serializers.ReadOnlyField()
    completed_stages = serializers.ReadOnlyField()

    class Meta:
        model  = Project
        fields = [
            'id', 'name', 'description', 'project_type', 'status',
            'client', 'client_name',
            'address', 'city', 'state', 'country',
            'contract_value', 'currency', 'management_fee_percent',
            'start_date', 'estimated_end_date', 'actual_end_date',
            'camera_stream_url', 'camera_online',
            'progress_percent', 'total_paid', 'total_stages', 'completed_stages',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_client_name(self, obj):
        return obj.client.full_name


class EOISubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EOISubmission
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone',
            'project_type', 'project_location', 'budget_range',
            'timeline', 'description', 'tc_accepted', 'status', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_tc_accepted(self, value):
        if not value:
            raise serializers.ValidationError('You must accept the Terms and Conditions.')
        return value

    def validate_status(self, value):
        allowed = ['pending', 'contacted', 'converted', 'declined']
        if value not in allowed:
            raise serializers.ValidationError(
                f'Status must be one of: {", ".join(allowed)}'
            )
        return value
