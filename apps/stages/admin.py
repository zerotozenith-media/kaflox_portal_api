from django.contrib import admin
from .models import StageTemplate, Stage, StageComment, SnagItem


@admin.register(StageTemplate)
class StageTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'project_type', 'default_order', 'is_active']
    list_editable = ['default_order', 'is_active']
    list_filter = ['project_type', 'is_active']


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'order', 'status', 'material_cost', 'labour_cost', 'actual_start', 'actual_end']
    list_filter = ['status']
    search_fields = ['name', 'project__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SnagItem)
class SnagItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'stage', 'raised_by', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
