from django.urls import path
from . import views

urlpatterns = [
    # Media
    path('',                  views.MediaListCreateView.as_view(), name='media-list'),
    path('<uuid:pk>/',        views.MediaDetailView.as_view(),     name='media-detail'),

    # Documents
    path('documents/',            views.DocumentListCreateView.as_view(), name='document-list'),
    path('documents/<uuid:pk>/',  views.DocumentDetailView.as_view(),     name='document-detail'),
]
