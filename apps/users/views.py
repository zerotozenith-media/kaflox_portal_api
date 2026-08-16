from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCreateSerializer, UserProfileSerializer

User = get_user_model()


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.SUPER_ADMIN


class IsAdminOrTeamMember(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [User.SUPER_ADMIN, User.TEAM_MEMBER]


class UserListCreateView(generics.ListCreateAPIView):
    """List: super admins or team members (e.g. to populate staff/client dropdowns).
    Create: super admins only."""

    def get_queryset(self):
        qs = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            roles = [r.strip() for r in role.split(',') if r.strip()]
            qs = qs.filter(role__in=roles)
        return qs.order_by('first_name', 'last_name')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsSuperAdmin()]
        return [IsAdminOrTeamMember()]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin: retrieve, update, or deactivate a user."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Authenticated user: view and update own profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def me(request):
    """Return current authenticated user."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def eoi_submit(request):
    """Handle EOI form submission -- creates showcase account."""
    from apps.projects.models import EOISubmission
    from apps.projects.serializers import EOISubmissionSerializer
    import secrets

    serializer = EOISubmissionSerializer(data=request.data)
    if serializer.is_valid():
        eoi = serializer.save()

        # Create showcase user account
        email = eoi.email
        if not User.objects.filter(email=email).exists():
            temp_password = secrets.token_urlsafe(10)
            user = User.objects.create_user(
                email=email,
                password=temp_password,
                first_name=eoi.first_name,
                last_name=eoi.last_name,
                role=User.EOI_PROSPECT,
            )
            eoi.showcase_user = user
            eoi.save()
            # TODO: Send welcome email with credentials via Azure Communication Services

        return Response({'message': 'EOI submitted. Showcase access granted.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)