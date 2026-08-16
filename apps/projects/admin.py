from django.contrib import admin
from .models import Project, EOISubmission


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client', 'project_type', 'status', 'contract_value', 'currency', 'progress_percent', 'start_date']
    list_filter = ['project_type', 'status', 'currency']
    search_fields = ['name', 'client__email', 'client__first_name', 'city']
    raw_id_fields = ['client']
    filter_horizontal = ['team_members']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Project Info', {'fields': ('name', 'description', 'project_type', 'status', 'client', 'team_members')}),
        ('Location', {'fields': ('address', 'city', 'state', 'country')}),
        ('Financials', {'fields': ('contract_value', 'currency', 'management_fee_percent')}),
        ('Timeline', {'fields': ('start_date', 'estimated_end_date', 'actual_end_date')}),
        ('Camera', {'fields': ('camera_stream_url', 'camera_online')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(EOISubmission)
class EOISubmissionAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'project_type', 'budget_range', 'status', 'created_at']
    list_filter = ['status', 'project_type']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['created_at']
    list_editable = ['status']
