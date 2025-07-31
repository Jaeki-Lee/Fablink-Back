from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from .serializers import LoginSerializer
from .services import AuthService


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    사용자 로그인 API
    POST /api/accounts/login/
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'message': '로그인 실패',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 비즈니스 로직을 서비스 레이어로 위임
        user = serializer.validated_data['user']
        result = AuthService.login_user(user.user_id, request.data.get('password'))
        
        return Response({
            'success': True,
            'message': '로그인 성공',
            'tokens': result['tokens'],
            'user': AuthService.get_user_info(result['user'])
        }, status=status.HTTP_200_OK)
        
    except serializers.ValidationError as e:
        return Response({
            'success': False,
            'message': str(e),
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    """
    현재 로그인된 사용자 정보 조회 API
    GET /api/accounts/user/
    """
    try:
        # 비즈니스 로직을 서비스 레이어로 위임
        user_data = AuthService.get_user_info(request.user)
        
        return Response({
            'success': True,
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'사용자 정보 조회 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        
        # 비즈니스 로직을 서비스 레이어로 위임
        result = AuthService.logout_user(refresh_token)
        
        return Response({
            'success': True,
            'message': result['message']
        }, status=status.HTTP_200_OK)
        
    except serializers.ValidationError as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'로그아웃 실패: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)
