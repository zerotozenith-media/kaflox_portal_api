from django.urls import path
from . import views

urlpatterns = [
    path('',                                      views.StageListView.as_view(),          name='stage-list'),
    path('templates/',                            views.StageTemplateListView.as_view(),  name='stage-template-list'),
    path('<uuid:pk>/',                            views.StageDetailView.as_view(),        name='stage-detail'),
    path('<uuid:stage_id>/comments/',             views.add_comment,                      name='stage-comment'),
    path('<uuid:stage_id>/accept/',               views.client_accept_stage,              name='stage-accept'),
    path('<uuid:stage_id>/staff/',                views.stage_assigned_staff,             name='stage-staff'),
    path('snags/',                                views.SnagItemListCreateView.as_view(), name='snag-list'),
    path('snags/<uuid:pk>/',                      views.SnagItemDetailView.as_view(),     name='snag-detail'),
]
