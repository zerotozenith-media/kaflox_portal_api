from rest_framework import serializers
from .models import ProjectMedia


class ProjectMediaSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    stage_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectMedia
        fields = [
            'id', 'project', 'stage', 'stage_name', 'uploaded_by', 'uploaded_by_name',
            'media_type', 'title', 'description', 'file', 'blob_url',
            'file_size', 'duration_seconds', 'storage_tier', 'created_at',
        ]
        read_only_fields = ['id', 'uploaded_by', 'blob_url', 'storage_tier', 'created_at']

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else None

    def get_stage_name(self, obj):
        return obj.stage.name if obj.stage else None
