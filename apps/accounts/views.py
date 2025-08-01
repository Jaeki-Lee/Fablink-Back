from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import (
    LoginSerializer, 
    DesignerSerializer,
    FactorySerializer,
    TokenRefreshSerializer
)
from .models import Designer, Factory


# ==================== 통합 로그인/로그아웃 ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    통합 로그인 API (Designer와 Factory 모두 지원)
    POST /api/accounts/login/
    
    Request Body:
    {
        "user_id": "user123",
        "password": "password123",
        "user_type": "designer" | "factory"
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': '로그인 실패',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = serializer.validated_data['user']
        user_type = serializer.validated_data['user_type']
        refresh = RefreshToken.for_user(user)
        
        # 사용자 정보 직렬화
        if user_type == 'designer':
            user_data = DesignerSerializer(user, context={'request': request}).data
        else:  # factory
            user_data = FactorySerializer(user, context={'request': request}).data
        
        return Response({
            'success': True,
            'message': f'{user_type} 로그인 성공',
            'user_type': user_type,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'로그인 실패: {str(e)}',
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    통합 로그아웃 API
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
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh_view(request):
    """
    JWT 토큰 갱신 API
    POST /api/accounts/token/refresh/
    """
    serializer = TokenRefreshSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': '토큰 갱신 실패',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': True,
        'message': '토큰 갱신 성공',
        'tokens': {
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh']
        }
    }, status=status.HTTP_200_OK)

# ==================== 디자이너 관련 ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def designer_profile_view(request):
    """
    디자이너 프로필 조회 API
    GET /api/accounts/designer/profile/
    """
    if not isinstance(request.user, Designer):
        return Response({
            'success': False,
            'message': '디자이너만 접근 가능합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        serializer = DesignerSerializer(request.user, context={'request': request})
        
        return Response({
            'success': True,
            'designer': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'디자이너 정보 조회 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== 공장주 관련 ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def factory_profile_view(request):
    """
    공장주 프로필 조회 API
    GET /api/accounts/factory/profile/
    """
    if not isinstance(request.user, Factory):
        return Response({
            'success': False,
            'message': '공장주만 접근 가능합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        serializer = FactorySerializer(request.user, context={'request': request})
        
        return Response({
            'success': True,
            'factory': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'공장주 정보 조회 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
