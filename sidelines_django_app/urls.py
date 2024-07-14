from django.urls import path
from .views import UserRecordView, FriendRequestView, FriendRequestActionView, TeamView, TeamInvitationView, TeamInvitationActionView

app_name = 'api'
urlpatterns = [
    path('users/', UserRecordView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserRecordView.as_view(), name='user-detail'),
    path('friend-requests/', FriendRequestView.as_view(), name='create_friend_request'),
    path('friend-requests/<str:request_type>/', FriendRequestView.as_view(), name='friend_requests'),
    path('friend-requests/<int:friend_request_id>/<str:action>/', FriendRequestActionView.as_view(), name='friend_request_action'),
    path('teams/', TeamView.as_view(), name='team-list'),
    path('teams/<int:team_id>/', TeamView.as_view(), name='team-detail'),
    path('team-invitations/', TeamInvitationView.as_view(), name='create-team-invitation'),
    path('team-invitations/<str:request_type>/', TeamInvitationView.as_view(), name='team-invitations'),
    path('team-invitations/<str:team_invitation_id>/<str:action>/', TeamInvitationActionView.as_view(), name='team_invitation_action'),
]
