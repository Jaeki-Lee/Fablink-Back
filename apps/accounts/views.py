from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    사용자 로그인 API
    POST /api/accounts/login/
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)

        return Response({
            'success': True,
            'message': '로그인 성공',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)

    return Response({
        'success': False,
        'message': '로그인 실패',
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    """
    현재 로그인된 사용자 정보 조회 API
    GET /api/accounts/user/
    """
    user_serializer = UserSerializer(request.user)
    return Response({
        'success': True,
        'user': user_serializer.data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    사용자 로그아웃 API
    POST /api/accounts/logout/
    
    Request Body:
    {
        "refresh": "your-refresh-token"
    }
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh 토큰이 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 토큰 블랙리스트에 추가
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'success': True,
            'message': '로그아웃 성공'
        }, status=status.HTTP_200_OK)
        
    except TokenError:
        return Response({
            'success': False,
            'message': '유효하지 않은 토큰입니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'로그아웃 실패: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
