from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from .serializers import LoginSerializer, UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny]) # 로그인은 인증 없이 접근 가능
def login_view(request):
    """
    사용자 로그인 API
    POST /api/accounts/login/
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        token, created = Token.objects.get_or_create(user=user)

        # 사용자 정보 직렬화
        user_serializer = UserSerializer(user)

        logger.info(f"유저 {user.username} 로그인 성공.")

        return Response({
            'success': True,
            'message': '로그인 성공',
            'token': token.key,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

    logger.info(f"로그인 실패: {serializer.errors}")

    return Response({
        'success': False,
        'message': '로그인 실패',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_info_view(request):
    """
    현재 로그인된 사용자 정보 조회 API
    GET /api/accounts/user/
    """
    if request.user.is_authenticated:
        user_serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'success': False,
        'message': '로그인이 필요합니다.'
    }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    """
    사용자 로그아웃 API
    POST /api/accounts/logout/
    """
    
    try:
        request.user.auth_token.delete()  # 토큰 삭제
        return Response({
            'success': True,
            'message': '로그아웃 성공'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'success': False,
            'message': '로그아웃 실패'
        }, status=status.HTTP_400_BAD_REQUEST)