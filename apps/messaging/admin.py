from django.contrib import admin
from .models import MessageThread, Message, Notification


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['project', 'subject', 'updated_at']
    search_fields = ['project__name', 'subject']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'channel', 'status', 'is_read', 'created_at']
    list_filter = ['notification_type', 'channel', 'status', 'is_read']
    search_fields = ['recipient__email', 'title']
