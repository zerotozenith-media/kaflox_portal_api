from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import ProjectMedia, ProjectDocument
from .serializers import ProjectMediaSerializer, ProjectDocumentSerializer

User = get_user_model()


class IsAdminOrTeamMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.SUPER_ADMIN, User.TEAM_MEMBER]


# ── MEDIA ─────────────────────────────────────────────────────────────────────

class MediaListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectMediaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user       = self.request.user
        project_id = self.request.query_params.get('project')
        stage_id   = self.request.query_params.get('stage')
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


# ── DOCUMENTS ─────────────────────────────────────────────────────────────────

class DocumentListCreateView(generics.ListCreateAPIView):
    """
    GET  -- list documents for a project (?project=id)
            Clients see only their own project's documents.
    POST -- upload a new document (admin/team member only)
    """
    serializer_class = ProjectDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user          = self.request.user
        project_id    = self.request.query_params.get('project')
        document_type = self.request.query_params.get('type')
        qs = ProjectDocument.objects.select_related('project', 'uploaded_by')
        if project_id:
            qs = qs.filter(project__id=project_id)
        if document_type:
            qs = qs.filter(document_type=document_type)
        # Clients only see documents for their own projects
        if user.role == User.CLIENT:
            qs = qs.filter(project__client=user)
        return qs.order_by('document_type', '-created_at')

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrTeamMember()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        uploaded = self.request.data.get('file')
        file_size = uploaded.size if uploaded and hasattr(uploaded, 'size') else 0
        serializer.save(uploaded_by=self.request.user, file_size=file_size)


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    -- retrieve a single document (client can access their own)
    DELETE -- delete a document (admin/team member only)
    """
    serializer_class = ProjectDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.CLIENT:
            return ProjectDocument.objects.filter(project__client=user)
        return ProjectDocument.objects.all()

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsAdminOrTeamMember()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx
