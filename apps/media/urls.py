from django.urls import path
from . import views

urlpatterns = [
    path('', views.MediaListCreateView.as_view(), name='media-list'),
    path('<uuid:pk>/', views.MediaDetailView.as_view(), name='media-detail'),
]
