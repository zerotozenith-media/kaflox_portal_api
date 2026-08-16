from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.staff.models import StaffMember
from .models import Stage, StageTemplate, StageComment, SnagItem
from .serializers import (
    StageSerializer, StageTemplateSerializer,
    StageCommentSerializer, SnagItemSerializer, AssignedStaffSerializer
)

User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.SUPER_ADMIN


class IsAdminOrTeamMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.SUPER_ADMIN, User.TEAM_MEMBER]


class StageTemplateListView(generics.ListCreateAPIView):
    queryset = StageTemplate.objects.filter(is_active=True)
    serializer_class = StageTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]


class StageListView(generics.ListCreateAPIView):
    serializer_class = StageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')
        qs = Stage.objects.select_related('project__client', 'template').prefetch_related('assigned_staff')
        if project_id:
            qs = qs.filter(project__id=project_id)
        if user.role == User.CLIENT:
            qs = qs.filter(project__client=user)
        elif user.role == User.TEAM_MEMBER:
            qs = qs.filter(project__team_members=user)
        return qs.order_by('order')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrTeamMember()]
        return [permissions.IsAuthenticated()]


class StageDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = StageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.CLIENT:
            return Stage.objects.filter(project__client=user).prefetch_related('assigned_staff')
        return Stage.objects.all().prefetch_related('assigned_staff')


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminOrTeamMember])
def stage_assigned_staff(request, stage_id):
    """
    GET    -- list staff assigned to this stage
    POST   -- assign a staff member { "staff_member": "<uuid>" }
    DELETE -- remove a staff member { "staff_member": "<uuid>" }
    """
    try:
        stage = Stage.objects.get(id=stage_id)
    except Stage.DoesNotExist:
        return Response({'error': 'Stage not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response(AssignedStaffSerializer(stage.assigned_staff.all(), many=True).data)

    staff_id = request.data.get('staff_member')
    if not staff_id:
        return Response({'error': 'staff_member is required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        staff = StaffMember.objects.get(id=staff_id)
    except StaffMember.DoesNotExist:
        return Response({'error': 'Staff member not found.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        if stage.assigned_staff.filter(id=staff_id).exists():
            return Response({'error': 'Staff member already assigned to this stage.'}, status=status.HTTP_400_BAD_REQUEST)
        stage.assigned_staff.add(staff)
        return Response(AssignedStaffSerializer(staff).data, status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        stage.assigned_staff.remove(staff)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_comment(request, stage_id):
    try:
        stage = Stage.objects.get(id=stage_id)
    except Stage.DoesNotExist:
        return Response({'error': 'Stage not found.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = StageCommentSerializer(
        data={'stage': stage.id, 'content': request.data.get('content', '')}
    )
    if serializer.is_valid():
        serializer.save(author=request.user, stage=stage)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def client_accept_stage(request, stage_id):
    try:
        stage = Stage.objects.get(id=stage_id, project__client=request.user)
    except Stage.DoesNotExist:
        return Response({'error': 'Stage not found.'}, status=status.HTTP_404_NOT_FOUND)
    stage.client_accepted    = True
    stage.client_accepted_at = timezone.now()
    stage.status             = Stage.COMPLETED
    stage.actual_end         = timezone.now().date()
    stage.save()
    return Response({'message': 'Stage accepted.'})


class SnagItemListCreateView(generics.ListCreateAPIView):
    serializer_class = SnagItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        stage_id = self.request.query_params.get('stage')
        return SnagItem.objects.filter(stage__id=stage_id) if stage_id else SnagItem.objects.none()

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user)


class SnagItemDetailView(generics.RetrieveUpdateAPIView):
    queryset = SnagItem.objects.all()
    serializer_class = SnagItemSerializer
    permission_classes = [IsAdminOrTeamMember]
