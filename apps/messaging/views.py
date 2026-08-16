from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import MessageThread, Message, Notification
from .serializers import MessageThreadSerializer, MessageSerializer, NotificationSerializer

User = get_user_model()

STAFF_ROLES = ['super_admin', 'team_member']


class ThreadListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get('project')
        qs = MessageThread.objects.filter(participants=user)
        if project_id:
            qs = qs.filter(project__id=project_id)
        return qs.order_by('-updated_at')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data.get('project')

        if project is None:
            raise ValidationError({'project': 'This field is required.'})

        if user.role == 'client' and project.client_id != user.id:
            raise PermissionDenied("You can only message about your own project.")
        if user.role == 'team_member' and not project.team_members.filter(id=user.id).exists():
            raise PermissionDenied("You are not assigned to this project.")

        thread = serializer.save()
        thread.participants.add(user)
        thread.participants.add(project.client)


class AllThreadsView(generics.ListAPIView):
    """GET /messages/threads/all/ -- for the admin 'view every conversation' inbox.

    super_admin: every thread, across all projects.
    team_member: every thread for projects they're assigned to, even ones
    they aren't yet a participant on (so they can discover and pick up
    unassigned conversations via the Agents tab).
    """
    serializer_class = MessageThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role not in STAFF_ROLES:
            raise PermissionDenied("Only staff can view all conversations.")

        if user.role == 'super_admin':
            qs = MessageThread.objects.all()
        else:
            qs = MessageThread.objects.filter(
                Q(project__team_members=user) | Q(participants=user)
            ).distinct()

        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project__id=project_id)

        return qs.order_by('-updated_at')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['request'] = self.request
        return ctx


class ThreadMessageListView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs['thread_id']
        user = self.request.user

        try:
            thread = MessageThread.objects.select_related('project').get(id=thread_id)
        except MessageThread.DoesNotExist:
            return Message.objects.none()

        # A staff member can read any thread for a project they're assigned to
        # (or any thread at all, if super_admin), even before being explicitly
        # added as a participant -- otherwise the admin inbox couldn't open
        # unassigned conversations.
        allowed = thread.participants.filter(id=user.id).exists()
        if not allowed and user.role == 'super_admin':
            allowed = True
        if not allowed and user.role == 'team_member':
            allowed = thread.project.team_members.filter(id=user.id).exists()

        if not allowed:
            return Message.objects.none()

        msgs = Message.objects.filter(thread__id=thread_id)
        msgs.exclude(sender=user).update(is_read=True, read_at=timezone.now())
        return msgs.order_by('created_at')

    def perform_create(self, serializer):
        thread_id = self.kwargs['thread_id']
        user = self.request.user

        try:
            thread = MessageThread.objects.select_related('project').get(id=thread_id)
        except MessageThread.DoesNotExist:
            raise PermissionDenied("Thread not found.")

        is_participant = thread.participants.filter(id=user.id).exists()
        if not is_participant:
            if user.role == 'super_admin':
                thread.participants.add(user)  # auto-join: super admin steps into any thread
            elif user.role == 'team_member' and thread.project.team_members.filter(id=user.id).exists():
                thread.participants.add(user)
            else:
                raise PermissionDenied("You are not part of this conversation.")

        message = serializer.save(sender=user, thread=thread)
        thread.save()

        recipients = thread.participants.exclude(id=user.id)
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                project=thread.project,
                notification_type=Notification.MESSAGE_RECEIVED,
                title=f'New message: {thread.subject or thread.project.name}',
                body=message.content[:200],
            )


class ThreadAgentView(generics.GenericAPIView):
    """POST { staff_member: <User id> } -- assigns a real User account (team_member or
    super_admin) as a messaging agent on this thread, via participants.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, thread_id):
        user = request.user
        if user.role not in STAFF_ROLES:
            raise PermissionDenied("Only staff can assign agents.")

        try:
            thread = MessageThread.objects.select_related('project').get(id=thread_id)
        except MessageThread.DoesNotExist:
            return Response({'error': 'Thread not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.role == 'team_member' and not thread.project.team_members.filter(id=user.id).exists():
            raise PermissionDenied("You are not assigned to this project.")

        staff_id = request.data.get('staff_member')
        if not staff_id:
            return Response({'staff_member': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            agent_user = User.objects.get(id=staff_id, role__in=STAFF_ROLES)
        except User.DoesNotExist:
            return Response({'error': 'Staff account not found.'}, status=status.HTTP_404_NOT_FOUND)

        thread.participants.add(agent_user)

        # Being assigned as a messaging agent should also grant visibility into
        # the project itself (Projects list, stages, etc.), which is driven by
        # project.team_members, not thread.participants.
        if agent_user.role == 'team_member':
            thread.project.team_members.add(agent_user)

        Notification.objects.create(
            recipient=agent_user,
            project=thread.project,
            notification_type=Notification.MESSAGE_RECEIVED,
            title=f'Assigned to conversation: {thread.subject or thread.project.name}',
            body=f'You have been assigned as a messaging agent for {thread.project.name}.',
        )

        return Response(
            MessageThreadSerializer(thread, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_thread_agent(request, thread_id, agent_id):
    user = request.user
    if user.role not in STAFF_ROLES:
        raise PermissionDenied("Only staff can remove agents.")

    try:
        thread = MessageThread.objects.select_related('project').get(id=thread_id)
    except MessageThread.DoesNotExist:
        return Response({'error': 'Thread not found.'}, status=status.HTTP_404_NOT_FOUND)

    if user.role == 'team_member' and not thread.project.team_members.filter(id=user.id).exists():
        raise PermissionDenied("You are not assigned to this project.")

    if str(thread.project.client_id) == str(agent_id):
        return Response({'error': 'Cannot remove the client from the thread.'}, status=status.HTTP_400_BAD_REQUEST)

    thread.participants.remove(agent_id)

    # If this was their last thread on this project, also drop them from
    # project.team_members -- otherwise leave project access intact, since
    # they may still be assigned to other conversations on the same project.
    project = thread.project
    still_has_thread_on_project = MessageThread.objects.filter(
        project=project, participants__id=agent_id
    ).exists()
    if not still_has_thread_on_project:
        project.team_members.remove(agent_id)

    return Response({'message': 'Agent removed.'})


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notif = Notification.objects.get(id=pk, recipient=request.user)
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save()
        return Response({'message': 'Marked as read.'})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)