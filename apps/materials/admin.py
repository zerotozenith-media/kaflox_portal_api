from django.contrib import admin
from .models import Supplier, MaterialCategory, Material, MaterialPrice, CostAnomalyFlag


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact_person', 'phone_primary', 'city', 'state', 'is_active']
    list_filter = ['is_active', 'state']
    search_fields = ['name', 'contact_person', 'phone_primary']


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']


@admin.register(MaterialPrice)
class MaterialPriceAdmin(admin.ModelAdmin):
    list_display = ['material', 'supplier', 'price', 'currency', 'effective_date', 'is_active']
    list_filter = ['currency', 'is_active', 'supplier']
    search_fields = ['material__name', 'supplier__name']
    date_hierarchy = 'effective_date'


@admin.register(CostAnomalyFlag)
class CostAnomalyFlagAdmin(admin.ModelAdmin):
    list_display = ['material', 'stage', 'submitted_price', 'database_price', 'variance_percent', 'status']
    list_filter = ['status']
    list_editable = ['status']
