from rest_framework import serializers
from .models import Supplier, MaterialCategory, Material, MaterialPrice, CostAnomalyFlag


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'phone_primary', 'phone_secondary', 'email', 'address', 'city', 'state', 'country', 'is_active']


class MaterialCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialCategory
        fields = ['id', 'name', 'description']


class MaterialPriceSerializer(serializers.ModelSerializer):
    supplier_name = serializers.SerializerMethodField()
    supplier_phone = serializers.SerializerMethodField()
    supplier_address = serializers.SerializerMethodField()

    class Meta:
        model = MaterialPrice
        fields = ['id', 'supplier', 'supplier_name', 'supplier_phone', 'supplier_address', 'price', 'currency', 'effective_date', 'is_active']

    def get_supplier_name(self, obj): return obj.supplier.name
    def get_supplier_phone(self, obj): return obj.supplier.phone_primary
    def get_supplier_address(self, obj): return f'{obj.supplier.address}, {obj.supplier.city}'


class MaterialSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    current_price = MaterialPriceSerializer(read_only=True)
    all_prices = MaterialPriceSerializer(source='prices', many=True, read_only=True)

    class Meta:
        model = Material
        fields = ['id', 'name', 'category', 'category_name', 'unit', 'description', 'is_active', 'current_price', 'all_prices']

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None


class CostAnomalyFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostAnomalyFlag
        fields = ['id', 'stage', 'material', 'submitted_price', 'database_price', 'variance_percent', 'status', 'admin_notes', 'created_at']
        read_only_fields = ['id', 'created_at']
