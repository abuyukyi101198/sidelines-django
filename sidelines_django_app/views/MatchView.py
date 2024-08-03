from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from sidelines_django_app.models import Match, MatchVote
from sidelines_django_app.serializers import MatchSerializer


class MatchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request, match_id=None):
        if match_id:
            return MatchView.get_single_match(match_id)

        return MatchView.get_all_matches()

    @staticmethod
    def get_single_match(match_id):
        try:
            match = Match.objects.get(pk=match_id)
            serializer = MatchSerializer(match)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Match.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def get_all_matches():
        matches = Match.objects.all()
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    @api_view(['POST'])
    def vote(request, match_id):
        profile = request.user.profile
        vote_response = request.data.get('vote')

        if vote_response not in dict(MatchVote.RESPONSE_CHOICES):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            match = Match.objects.get(pk=match_id)
        except Match.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not match.admin_approved:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            match_vote = MatchVote.objects.get(match=match, profile=profile)
        except MatchVote.DoesNotExist:
            match_vote = MatchVote(match=match, profile=profile)

        match_vote.response = vote_response
        match_vote.save()

        return Response(status=status.HTTP_200_OK)
