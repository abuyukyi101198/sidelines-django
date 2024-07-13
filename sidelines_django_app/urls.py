from django.urls import path
from .views import UserRecordView, FriendRequestView, AcceptFriendRequestView, IgnoreFriendRequestView

app_name = 'api'
urlpatterns = [
    path('users/', UserRecordView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserRecordView.as_view(), name='user-detail'),
    path('<int:profile_id>/friend-requests/<str:request_type>/', FriendRequestView.as_view(), name='friend_requests'),
    path('<int:profile_id>/friend-requests/', FriendRequestView.as_view(), name='create_friend_request'),
    path('<int:profile_id>/friend-requests/<int:friend_request_id>/accept/', AcceptFriendRequestView.as_view(),
         name='accept_friend_request'),
    path('<int:profile_id>/friend-requests/<int:friend_request_id>/ignore/', IgnoreFriendRequestView.as_view(),
         name='ignore_friend_request'),
]
