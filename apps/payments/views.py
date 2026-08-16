import logging
import hmac
import hashlib
import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Payment, RefundRequest
from apps.stages.models import Stage

logger = logging.getLogger('kaflox')


class PaymentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = self.request.user
        from .serializers import PaymentSerializer
        if user.role == User.SUPER_ADMIN:
            return Payment.objects.all().select_related('project__client', 'stage')
        elif user.role == User.CLIENT:
            return Payment.objects.filter(client=user).select_related('project', 'stage')
        return Payment.objects.none()

    def get_serializer_class(self):
        from .serializers import PaymentSerializer
        return PaymentSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def initiate_payment(request, stage_id):
    """Initiate a Flutterwave payment for a project stage."""
    try:
        stage = Stage.objects.get(id=stage_id, project__client=request.user)
    except Stage.DoesNotExist:
        return Response({'error': 'Stage not found.'}, status=status.HTTP_404_NOT_FOUND)

    if stage.status != Stage.AWAITING_PAYMENT:
        return Response({'error': 'Stage is not awaiting payment.'}, status=status.HTTP_400_BAD_REQUEST)

    total = float(stage.total_amount_due)
    currency = stage.project.currency

    # Create payment record
    payment = Payment.objects.create(
        project=stage.project,
        stage=stage,
        client=request.user,
        amount=total,
        currency=currency,
        material_cost=stage.material_cost,
        labour_cost=stage.labour_cost,
        management_fee=stage.management_fee,
        management_fee_percent=stage.project.management_fee_percent,
        status=Payment.PENDING,
    )

    # Initiate Flutterwave payment
    payload = {
        'tx_ref': str(payment.id),
        'amount': total,
        'currency': currency,
        'redirect_url': f'https://portal.kafloxengineering.com/payments/callback',
        'customer': {
            'email': request.user.email,
            'name': request.user.full_name,
            'phonenumber': request.user.phone,
        },
        'meta': {
            'payment_id': str(payment.id),
            'stage_id': str(stage.id),
            'project_id': str(stage.project.id),
        },
        'customizations': {
            'title': 'Kaflox Engineering',
            'description': f'Payment for {stage.name}',
            'logo': 'https://portal.kafloxengineering.com/logo.png',
        },
    }

    headers = {
        'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(
            f'{settings.FLUTTERWAVE_BASE_URL}/payments',
            json=payload, headers=headers, timeout=15
        )
        data = response.json()
        if data.get('status') == 'success':
            payment.flutterwave_ref = str(payment.id)
            payment.status = Payment.PROCESSING
            payment.save()
            return Response({'payment_link': data['data']['link'], 'payment_id': str(payment.id)})
        else:
            payment.status = Payment.FAILED
            payment.save()
            return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.error(f'Flutterwave error: {e}')
        return Response({'error': 'Payment gateway error.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def flutterwave_webhook(request):
    """Handle Flutterwave payment webhook."""
    secret_hash = settings.FLUTTERWAVE_SECRET_KEY
    signature = request.headers.get('verif-hash')

    if not signature or signature != secret_hash:
        return Response({'error': 'Invalid signature.'}, status=status.HTTP_401_UNAUTHORIZED)

    data = request.data
    if data.get('event') == 'charge.completed' and data.get('data', {}).get('status') == 'successful':
        tx_ref = data['data'].get('tx_ref')
        try:
            payment = Payment.objects.get(id=tx_ref)
            payment.status = Payment.CONFIRMED
            payment.gateway_response = data
            payment.flutterwave_tx_id = str(data['data'].get('id', ''))
            payment.confirmed_at = timezone.now()
            payment.save()

            # Unlock the stage
            if payment.stage:
                payment.stage.status = Stage.IN_PROGRESS
                payment.stage.actual_start = timezone.now().date()
                payment.stage.save()

            logger.info(f'Payment confirmed: {payment.id}')
        except Payment.DoesNotExist:
            logger.warning(f'Webhook: payment not found for tx_ref {tx_ref}')

    return Response({'status': 'ok'})
