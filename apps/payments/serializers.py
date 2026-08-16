from rest_framework import serializers
from .models import Payment, RefundRequest


class PaymentSerializer(serializers.ModelSerializer):
    stage_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = [
            'id', 'project', 'project_name', 'stage', 'stage_name',
            'amount', 'currency', 'material_cost', 'labour_cost',
            'management_fee', 'management_fee_percent',
            'status', 'payment_method', 'flutterwave_ref',
            'confirmed_at', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'confirmed_at']

    def get_stage_name(self, obj):
        return obj.stage.name if obj.stage else None

    def get_project_name(self, obj):
        return obj.project.name


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = [
            'id', 'project', 'reason', 'amount_paid',
            'deduction_effort', 'deduction_processing', 'net_refund',
            'status', 'processing_deadline', 'created_at',
        ]
        read_only_fields = [
            'id', 'net_refund', 'status',
            'deduction_effort', 'deduction_processing',
            'processing_deadline', 'created_at',
        ]
