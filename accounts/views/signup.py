from accounts.views.base import Base
from accounts.auth import Authentication
from accounts.serializers import UserSerializer

from rest_framework.response import Response
from rest_framework.exceptions import APIException


class Signup(Base): 

    def post(self, request):
        
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('password')

        if not name or not email or not password:
            return Response({"error": "Nome, email e senha são obrigatórios"}, status=400)

        try:
            user = Authentication.signup(self, name=name, email=email, password=password)
        except APIException as e:
            return Response({"error": str(e)}, status=400)

        if not user:
            return Response({"error": "Erro ao criar usuário"}, status=500)

        serializer = UserSerializer(user)

        return Response({"user": serializer.data}, status=201)