from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from .models import Supplier, MaterialCategory, Material, MaterialPrice, CostAnomalyFlag
from .serializers import SupplierSerializer, MaterialCategorySerializer, MaterialSerializer, MaterialPriceSerializer, CostAnomalyFlagSerializer

User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.SUPER_ADMIN


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.filter(is_active=True)
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]


class SupplierDetailView(generics.RetrieveUpdateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsSuperAdmin]


class MaterialListCreateView(generics.ListCreateAPIView):
    serializer_class = MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'category__name']

    def get_queryset(self):
        qs = Material.objects.filter(is_active=True).select_related('category')
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        if search:
            qs = qs.filter(name__icontains=search)
        if category:
            qs = qs.filter(category__id=category)
        return qs

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]


class MaterialDetailView(generics.RetrieveUpdateAPIView):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsSuperAdmin]


class MaterialPriceCreateView(generics.CreateAPIView):
    """POST /materials/<material_id>/prices/ -- adds a new price point for a material.

    Material.current_price always resolves to the most recent active price by
    effective_date, so no explicit deactivation of older MaterialPrice rows is
    needed here -- creating a new one with today's (or a later) effective_date
    is enough for it to become the current price automatically.
    """
    serializer_class = MaterialPriceSerializer
    permission_classes = [IsSuperAdmin]

    def perform_create(self, serializer):
        material_id = self.kwargs['material_id']
        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            raise NotFound('Material not found.')
        serializer.save(material=material, updated_by=self.request.user)


class CategoryListView(generics.ListCreateAPIView):
    queryset = MaterialCategory.objects.all()
    serializer_class = MaterialCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CostAnomalyListView(generics.ListAPIView):
    serializer_class = CostAnomalyFlagSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return CostAnomalyFlag.objects.filter(status=CostAnomalyFlag.OPEN).order_by('-created_at')


class CostAnomalyDetailView(generics.RetrieveUpdateAPIView):
    queryset = CostAnomalyFlag.objects.all()
    serializer_class = CostAnomalyFlagSerializer
    permission_classes = [IsSuperAdmin]