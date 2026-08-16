from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
from .models import Project, EOISubmission
from .serializers import ProjectSerializer, EOISubmissionSerializer

User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.SUPER_ADMIN


class IsAdminOrTeamMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            User.SUPER_ADMIN, User.TEAM_MEMBER
        ]


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.SUPER_ADMIN:
            return Project.objects.all().select_related('client')
        elif user.role == User.TEAM_MEMBER:
            return user.assigned_projects.all().select_related('client')
        elif user.role == User.CLIENT:
            return Project.objects.filter(client=user).select_related('client')
        return Project.objects.none()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return [permissions.IsAuthenticated()]


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == User.SUPER_ADMIN:
            return Project.objects.all()
        elif user.role == User.TEAM_MEMBER:
            return user.assigned_projects.all()
        elif user.role == User.CLIENT:
            return Project.objects.filter(client=user)
        return Project.objects.none()


class EOIListView(generics.ListAPIView):
    queryset = EOISubmission.objects.all().order_by('-created_at')
    serializer_class = EOISubmissionSerializer
    permission_classes = [IsSuperAdmin]


class EOIDetailView(generics.RetrieveUpdateAPIView):
    """
    GET  -- retrieve a single EOI
    PATCH -- update EOI status (contacted, converted, declined)

    When status is set to 'converted':
    - A new client user account is automatically created using the EOI email,
      first name, and last name.
    - A temporary password is generated and stored.
    - The EOI status is updated to 'converted'.
    - The created user ID is returned in the response.

    Note: In production, send the temporary password to the client via email
    using Azure Communication Services.
    """
    queryset = EOISubmission.objects.all()
    serializer_class = EOISubmissionSerializer
    permission_classes = [IsSuperAdmin]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        new_status = request.data.get('status')

        # Handle conversion: create a client user account
        if new_status == 'converted' and instance.status != 'converted':
            # Check if user with this email already exists
            existing = User.objects.filter(email=instance.email).first()
            if existing:
                # Already has an account -- just update EOI status
                serializer = self.get_serializer(instance, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({
                    **serializer.data,
                    'message': 'EOI converted. A user account with this email already exists.',
                    'user_id': str(existing.id),
                })

            # Generate a temporary password
            temp_password = get_random_string(12)

            # Create the client user account from EOI data
            new_user = User.objects.create_user(
                email=instance.email,
                first_name=instance.first_name,
                last_name=instance.last_name,
                phone=instance.phone or '',
                role='client',
                password=temp_password,
                is_active=True,
            )

            # Update EOI status
            instance.status = 'converted'
            instance.save()

            # TODO: Send temp_password to client via email
            # When Azure Communication Services is configured:
            # send_welcome_email(instance.email, instance.first_name, temp_password)

            return Response({
                **EOISubmissionSerializer(instance).data,
                'message': f'Client account created for {instance.email}. Temporary password generated.',
                'user_id': str(new_user.id),
                'temp_password': temp_password,  # Remove this in production, send via email instead
            }, status=status.HTTP_200_OK)

        # For contacted and declined -- just update the status
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def document_download(request, project_id, doc_key):
    """Return a signed Azure Blob URL for a project document."""
    try:
        if request.user.role == 'client':
            project = Project.objects.get(id=project_id, client=request.user)
        else:
            project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)

    from django.conf import settings
    try:
        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta
        blob_name    = f'documents/{project_id}/{doc_key}.pdf'
        account_name = settings.AZURE_ACCOUNT_NAME
        account_key  = settings.AZURE_ACCOUNT_KEY
        container    = settings.AZURE_DOCUMENTS_CONTAINER

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(minutes=15),
        )
        url = f'https://{account_name}.blob.core.windows.net/{container}/{blob_name}?{sas_token}'
        return Response({'url': url})
    except Exception:
        return Response(
            {'error': 'Document not yet uploaded to storage. Please contact your Kaflox project manager.'},
            status=status.HTTP_404_NOT_FOUND
        )
