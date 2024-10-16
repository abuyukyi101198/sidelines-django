from django.urls import path
from .views import *
from sidelines_django_app.views.authentication.SignUpView import username_unique_check

app_name = 'api'
urlpatterns = [
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('username-unique-check/', username_unique_check, name='username-unique-check'),
    path('verify-token/', VerifyTokenView.as_view(), name='verify-token'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/friends/', FriendsView.as_view(), name='profile-friends'),
    path('profile/search/', ProfileSearchView.as_view(), name='profile-search'),

    path('friend-requests/', FriendRequestView.as_view(), name='create-friend-request'),
    path('friend-requests/<int:request_id>/', FriendRequestView.as_view(), name='friend-request-detail'),
    path('friend-requests/<str:request_type>/', FriendRequestView.as_view(), name='friend-request-list'),
    path('friend-requests/<int:request_id>/<str:action>/', FriendRequestView.as_view(), name='friend-request-action'),

    path('friend-requests/unfriend/<int:profile_id>/', FriendRequestView.unfriend, name='unfriend'),

    path('team-invitations/', TeamInvitationView.as_view(), name='create-team-invitation'),
    path('team-invitations/<int:request_id>/', TeamInvitationView.as_view(), name='team-invitation-detail'),
    path('team-invitations/<str:request_type>/', TeamInvitationView.as_view(), name='team-invitation-list'),
    path('team-invitations/<int:request_id>/<str:action>/', TeamInvitationView.as_view(), name='team-invitation-action'),

    path('teams/', TeamView.as_view(), name='team-list'),
    path('teams/<int:team_id>/', TeamView.as_view(), name='team-detail'),
    path('teams/<int:team_id>/leave/', TeamView.leave, name='leave-team'),
    path('teams/<int:team_id>/remove-member/<int:member_id>/', TeamView.remove_member, name='remove-member'),
    path('teams/<int:team_id>/member/<int:member_id>/<str:action>/', TeamView.promote_or_demote_member, name='promote-demote-member'),

    path('match-invitations/', MatchInvitationView.as_view(), name='create-match-invitation'),
    path('match-invitations/<int:request_id>/', MatchInvitationView.as_view(), name='match-invitation-detail'),
    path('match-invitations/<str:request_type>/', MatchInvitationView.as_view(), name='match-invitation-list'),
    path('match-invitations/<int:request_id>/<str:action>/', MatchInvitationView.as_view(), name='match-invitation-action'),

    path('matches/', MatchView.as_view(), name='match-list'),
    path('matches/<int:match_id>/', MatchView.as_view(), name='match-detail'),

    path('matches/vote/<int:match_id>/', MatchView.vote, name='vote'),
]

urlpatterns_new = [
    'sign-up', # POST
    'sign-in', # POST
    'sign-out', # POST

    'profile', # PUT | DELETE - ProfileSetupSerializer, ProfileEditSerializer
    'profile/<int:profile_id>', # GET - ProfileSerializer
    'profile/friends', # GET - FriendsSerializer

    'profile/matches', # GET - MatchesSerializer
    'profile/teams', # GET - TeamsSerializer
]
