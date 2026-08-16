from rest_framework import serializers
from .models import MessageThread, Message, Notification


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    sender_role = serializers.SerializerMethodField()
    sender_job_title = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id', 'thread', 'sender', 'sender_name', 'sender_role', 'sender_job_title',
            'content', 'is_read', 'read_at', 'attachment', 'created_at',
        ]
        read_only_fields = ['id', 'thread', 'sender', 'is_read', 'read_at', 'created_at']

    def get_sender_name(self, obj):
        return obj.sender.full_name

    def get_sender_role(self, obj):
        return obj.sender.role

    def get_sender_job_title(self, obj):
        # Optional field on your User model -- adjust/remove if it doesn't exist.
        return getattr(obj.sender, 'job_title', None)


class MessageThreadSerializer(serializers.ModelSerializer):
    last_message_preview = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    agents = serializers.SerializerMethodField()

    class Meta:
        model = MessageThread
        fields = ['id', 'project', 'project_name', 'subject', 'last_message_preview', 'unread_count', 'agents', 'updated_at']
        read_only_fields = ['id', 'updated_at']

    def get_last_message_preview(self, obj):
        msg = obj.last_message
        return msg.content[:80] if msg else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request:
            return 0
        user = request.user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()

    def get_project_name(self, obj):
        return obj.project.name

    def get_agents(self, obj):
        """'Agents' = staff (non-client) participants -- real User accounts that can
        actually log in and reply. NOT thread.agents (M2M to staff.StaffMember,
        which has no login and can't message)."""
        staff = obj.participants.exclude(id=obj.project.client_id)
        return [
            {
                'id': str(u.id),
                'full_name': u.full_name,
                'role_name': getattr(u, 'get_role_display', lambda: u.role)(),
            }
            for u in staff
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'project', 'notification_type', 'title', 'body', 'channel', 'status', 'is_read', 'read_at', 'created_at']
        read_only_fields = ['id', 'created_at']