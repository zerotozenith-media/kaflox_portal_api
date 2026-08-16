from django.urls import path
from . import views

urlpatterns = [
    path('', views.MaterialListCreateView.as_view(), name='material-list'),
    path('<uuid:pk>/', views.MaterialDetailView.as_view(), name='material-detail'),
    path('<uuid:material_id>/prices/', views.MaterialPriceCreateView.as_view(), name='material-price-create'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('suppliers/', views.SupplierListCreateView.as_view(), name='supplier-list'),
    path('suppliers/<uuid:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    path('anomalies/', views.CostAnomalyListView.as_view(), name='anomaly-list'),
    path('anomalies/<uuid:pk>/', views.CostAnomalyDetailView.as_view(), name='anomaly-detail'),
]