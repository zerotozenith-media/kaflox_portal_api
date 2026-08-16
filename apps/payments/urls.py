from django.urls import path
from . import views

urlpatterns = [
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('initiate/<uuid:stage_id>/', views.initiate_payment, name='payment-initiate'),
    path('webhook/flutterwave/', views.flutterwave_webhook, name='flutterwave-webhook'),
]
