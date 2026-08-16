from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import StaffRole, StaffMember, AttendanceRecord, MaterialIssuance, DeliveryLog
from .serializers import StaffRoleSerializer, StaffMemberSerializer, AttendanceSerializer, MaterialIssuanceSerializer, DeliveryLogSerializer

User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.SUPER_ADMIN


class IsAdminOrTeamMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.SUPER_ADMIN, User.TEAM_MEMBER]


class StaffRoleListCreateView(generics.ListCreateAPIView):
    queryset = StaffRole.objects.filter(is_active=True).order_by('order')
    serializer_class = StaffRoleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]


class StaffMemberListCreateView(generics.ListCreateAPIView):
    serializer_class = StaffMemberSerializer
    permission_classes = [IsAdminOrTeamMember]

    def get_queryset(self):
        qs = StaffMember.objects.select_related('role')
        staff_type = self.request.query_params.get('type')
        if staff_type:
            qs = qs.filter(staff_type=staff_type)
        return qs.filter(status=StaffMember.ACTIVE)


class StaffMemberDetailView(generics.RetrieveUpdateAPIView):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
    permission_classes = [IsAdminOrTeamMember]


class AttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeamMember]

    def get_queryset(self):
        qs = AttendanceRecord.objects.select_related('staff_member', 'project')
        project = self.request.query_params.get('project')
        date = self.request.query_params.get('date')
        if project:
            qs = qs.filter(project__id=project)
        if date:
            qs = qs.filter(date=date)
        return qs.order_by('-date')

    def perform_create(self, serializer):
        serializer.save(logged_by=self.request.user)


class DeliveryLogListCreateView(generics.ListCreateAPIView):
    serializer_class = DeliveryLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = DeliveryLog.objects.select_related('supplier', 'material', 'project')
        project = self.request.query_params.get('project')
        if project:
            qs = qs.filter(project__id=project)
        if user.role == User.CLIENT:
            qs = qs.filter(project__client=user)
        return qs.order_by('-delivery_date')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrTeamMember()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(logged_by=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def client_confirm_delivery(request, pk):
    try:
        delivery = DeliveryLog.objects.get(id=pk, project__client=request.user)
        delivery.client_confirmed = True
        delivery.save()
        return Response({'message': 'Delivery confirmed.'})
    except DeliveryLog.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
