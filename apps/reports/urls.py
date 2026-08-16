from django.urls import path
from . import views

urlpatterns = [
    path('progress/<uuid:project_id>/', views.progress_report, name='report-progress'),
    path('payments/<uuid:project_id>/', views.payment_report, name='report-payments'),
]
