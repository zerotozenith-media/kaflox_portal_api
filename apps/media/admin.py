from django.contrib import admin
from .models import ProjectMedia


@admin.register(ProjectMedia)
class ProjectMediaAdmin(admin.ModelAdmin):
    list_display = ['project', 'stage', 'media_type', 'storage_tier', 'uploaded_by', 'created_at']
    list_filter = ['media_type', 'storage_tier']
    search_fields = ['project__name', 'title']
    readonly_fields = ['created_at', 'blob_url']
