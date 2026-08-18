from rest_framework import serializers
from .models import ProjectMedia, ProjectDocument


class ProjectMediaSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    stage_name       = serializers.SerializerMethodField()

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


class ProjectDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name    = serializers.SerializerMethodField()
    document_type_label = serializers.SerializerMethodField()
    file_url            = serializers.SerializerMethodField()

    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'project', 'uploaded_by', 'uploaded_by_name',
            'name', 'document_type', 'document_type_label', 'description',
            'file', 'file_url', 'blob_url', 'file_size',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'uploaded_by', 'blob_url', 'created_at', 'updated_at']

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.full_name if obj.uploaded_by else None

    def get_document_type_label(self, obj):
        return obj.get_document_type_display()

    def get_file_url(self, obj):
        # Prefer the Azure blob URL if present, otherwise the local file URL
        if obj.blob_url:
            return obj.blob_url
        if obj.file:
            request = self.context.get('request')
            url = obj.file.url
            return request.build_absolute_uri(url) if request else url
        return None
