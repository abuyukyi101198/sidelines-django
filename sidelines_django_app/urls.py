from django.urls import path
from .views import *

app_name = 'api'
urlpatterns = [
    path('users/', UserRecordView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserRecordView.as_view(), name='user-detail'),

    path('friend-requests/', FriendRequestView.as_view(), name='create-friend-request'),
    path('friend-requests/<int:friend_request_id>/', FriendRequestView.as_view(), name='friend-request-detail'),
    path('friend-requests/<str:friend_request_type>/', FriendRequestView.as_view(), name='friend-request-list'),
    path('friend-requests/<int:friend_request_id>/<str:action>/', FriendRequestView.as_view(), name='friend-request-action'),

    path('team-invitations/', TeamInvitationView.as_view(), name='create-team-invitation'),
    path('team-invitations/<int:team_invitation_id>/', TeamInvitationView.as_view(), name='team-invitation-detail'),
    path('team-invitations/<str:team_invitation_type>/', TeamInvitationView.as_view(), name='team-invitation-list'),
    path('team-invitations/<int:team_invitation_id>/<str:action>/', TeamInvitationView.as_view(), name='team-invitation-action'),

    path('teams/', TeamView.as_view(), name='team-list'),
    path('teams/<int:team_id>/', TeamView.as_view(), name='team-detail'),
    path('teams/<int:team_id>/leave/', LeaveTeamView.as_view(), name='leave-team'),
    path('teams/<int:team_id>/member/<int:member_id>/<str:action>/', PromoteDemoteMemberView.as_view(), name='promote-demote-member'),
    path('teams/<int:team_id>/remove-member/<int:member_id>/', RemoveMemberView.as_view(), name='remove-member'),
]
