from accounts.views.base import Base
from accounts.auth import Authentication
from accounts.serializers import UserSerializer

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authentication import TokenAuthentication

class Signin(Base):
    authentication_classes = [TokenAuthentication]

    def post(self, request): 

        email = request.data.get('email')         
        password = request.data.get('password')   

        user = Authentication.signin(self, email=email, password=password)  

        token = RefreshToken.for_user(user)       

        enterprise = self.get_enterprise_user(user.id)  
                
        serializer = UserSerializer(user)   


        return Response({             
            "user": serializer.data,             
            "enterprise": enterprise,             
            "refresh": str(token),             
            "access": str(token.access_token)         
        })