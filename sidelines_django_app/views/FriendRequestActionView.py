from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import FriendRequest


class FriendRequestActionView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def post(request, friend_request_id, action):
        try:
            friend_request = FriendRequest.objects.get(pk=friend_request_id)
            return FriendRequestActionView.handle_action(request.user, friend_request, action)
        except FriendRequest.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def handle_action(user, friend_request, action):
        if action == 'accept':
            return FriendRequestActionView.accept_request(user, friend_request)
        elif action == 'ignore':
            return FriendRequestActionView.ignore_request(user, friend_request)
        elif action == 'withdraw':
            return FriendRequestActionView.withdraw_request(user, friend_request)
        else:
            return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def accept_request(user, friend_request):
        if friend_request.to_profile.user != user:
            return Response({'detail': 'You can only accept friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.accept()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def ignore_request(user, friend_request):
        if friend_request.to_profile.user != user:
            return Response({'detail': 'You can only ignore friend requests sent to you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.ignore()
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def withdraw_request(user, friend_request):
        if friend_request.from_profile.user != user:
            return Response({'detail': 'You can only withdraw friend requests sent by you.'},
                            status=status.HTTP_403_FORBIDDEN)
        friend_request.delete()
        return Response(status=status.HTTP_200_OK)