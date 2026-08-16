from django.urls import path
from . import views

urlpatterns = [
    path('threads/all/', views.AllThreadsView.as_view(), name='thread-list-all'),
    path('threads/', views.ThreadListCreateView.as_view(), name='thread-list'),
    path('threads/<uuid:thread_id>/messages/', views.ThreadMessageListView.as_view(), name='thread-messages'),
    path('threads/<uuid:thread_id>/agents/', views.ThreadAgentView.as_view(), name='thread-agents'),
    path('threads/<uuid:thread_id>/agents/<uuid:agent_id>/', views.remove_thread_agent, name='thread-agent-remove'),
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/<uuid:pk>/read/', views.mark_notification_read, name='notification-read'),
]