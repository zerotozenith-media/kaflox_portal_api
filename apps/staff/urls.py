from django.urls import path
from . import views

urlpatterns = [
    path('roles/', views.StaffRoleListCreateView.as_view(), name='staff-role-list'),
    path('', views.StaffMemberListCreateView.as_view(), name='staff-list'),
    path('<uuid:pk>/', views.StaffMemberDetailView.as_view(), name='staff-detail'),
    path('attendance/', views.AttendanceListCreateView.as_view(), name='attendance-list'),
    path('deliveries/', views.DeliveryLogListCreateView.as_view(), name='delivery-list'),
    path('deliveries/<uuid:pk>/confirm/', views.client_confirm_delivery, name='delivery-confirm'),
]
