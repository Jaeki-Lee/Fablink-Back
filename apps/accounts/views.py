from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import UserSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        id = request.data.get('id')
        password = request.data.get('password')
        user_type = request.data.get('userType')
        
        # 사용자 인증
        user = authenticate(username=id, password=password)
        
        if user is None:
            return Response(
                {"message": "아이디 또는 비밀번호가 일치하지 않습니다."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 사용자 타입 확인 (프로필 모델에서 확인하거나 그룹으로 확인)
        if hasattr(user, 'profile') and user.profile.user_type != user_type:
            return Response(
                {"message": "사용자 타입이 일치하지 않습니다."}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # 토큰 생성 (기본 토큰 인증 사용)
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            "message": "로그인 성공",
            "user": {
                "id": user.username,
                "userType": user_type,
                "loginTime": request.data.get('loginTime', None)
            },
            "token": token.key
        })

class UserInfoView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)