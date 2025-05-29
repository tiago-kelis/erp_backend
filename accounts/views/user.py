from accounts.views.base import Base
from accounts.models import User
from accounts.serializers import UserSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework import status

class GetUser(Base):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)

        enterprise = self.get_enterprise_user(user.id)  # Corrigindo chamada de função

        serializer = UserSerializer(user)

        return Response({
            "user": serializer.data,
            "enterprise": enterprise
        }, status=status.HTTP_200_OK)