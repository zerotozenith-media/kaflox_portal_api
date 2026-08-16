from django.contrib import admin
from .models import Payment, RefundRequest


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'project', 'stage', 'client', 'amount', 'currency', 'status', 'confirmed_at']
    list_filter = ['status', 'currency']
    search_fields = ['project__name', 'client__email', 'flutterwave_ref']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at']


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ['project', 'client', 'amount_paid', 'net_refund', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
