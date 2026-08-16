from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list'),
    path('<uuid:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('eoi/', views.EOIListView.as_view(), name='eoi-list'),
    path('eoi/<uuid:pk>/', views.EOIDetailView.as_view(), name='eoi-detail'),
]

from . import views as project_views
urlpatterns += [
    path('<uuid:project_id>/documents/<str:doc_key>/', project_views.document_download, name='document-download'),
]
