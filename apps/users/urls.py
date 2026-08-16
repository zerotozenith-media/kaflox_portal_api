from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.me, name='user-me'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('', views.UserListCreateView.as_view(), name='user-list'),
    path('<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('eoi/', views.eoi_submit, name='eoi-submit'),
]
