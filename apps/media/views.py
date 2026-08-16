from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import ProjectMedia
from .serializers import ProjectMediaSerializer

User = get_user_model()


class IsAdminOrTeamMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.SUPER_ADMIN, User.TEAM_MEMBER]


class MediaListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')
        stage_id = self.request.query_params.get('stage')
        media_type = self.request.query_params.get('type')
        qs = ProjectMedia.objects.exclude(storage_tier=ProjectMedia.DELETED)
        if project_id:
            qs = qs.filter(project__id=project_id)
        if stage_id:
            qs = qs.filter(stage__id=stage_id)
        if media_type:
            qs = qs.filter(media_type=media_type)
        if user.role == User.CLIENT:
            qs = qs.filter(project__client=user)
        return qs.order_by('-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrTeamMember()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class MediaDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ProjectMediaSerializer
    permission_classes = [IsAdminOrTeamMember]

    def get_queryset(self):
        return ProjectMedia.objects.all()
