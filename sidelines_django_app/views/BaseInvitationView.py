from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class BaseInvitationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    model = None
    serializer_class = None

    def get(self, request, request_type=None, request_id=None):
        if request_id is not None:
            return self.get_single_request(request_id)

        profile = request.user.profile
        return self.get_all_requests(profile, request_type)

    def get_single_request(self, request_id):
        try:
            request_obj = self.model.objects.get(pk=request_id)
            serializer = self.serializer_class(request_obj)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except self.model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_all_requests(self, profile, request_type):
        if request_type == 'sent':
            requests = self.model.objects.filter(from_profile=profile)
        elif request_type == 'received':
            requests = self.model.objects.filter(to_profile=profile)
        else:
            return Response({'detail': 'Invalid request type.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def put(self, request, request_id, action):
        profile = request.user.profile
        try:
            request_obj = self.model.objects.get(pk=request_id)
            if request_obj.to_profile != profile:
                return Response({'detail': 'You can only accept/ignore requests sent to you.'},
                                status=status.HTTP_403_FORBIDDEN)
            if action == 'accept':
                request_obj.accept()
            elif action == 'ignore':
                request_obj.ignore()
            else:
                return Response({'detail': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)
        except self.model.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, request_id):
        profile = request.user.profile

        try:
            request_obj = self.model.objects.get(pk=request_id)
        except self.model.DoesNotExist:
            return Response({'detail': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request_obj.from_profile != profile:
            return Response({'detail': 'You can only withdraw requests sent by you.'}, status=status.HTTP_403_FORBIDDEN)
        request_obj.delete()
        return Response(status=status.HTTP_200_OK)
