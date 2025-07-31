from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    LoginSerializer, 
    UserRegistrationSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer,
    TokenRefreshSerializer,
    UserListSerializer
)
from .services import AuthService, UserService



@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    사용자 로그인 API
    POST /api/accounts/login/
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.validated_data['user']
            
            # 비즈니스 로직을 서비스로 위임
            result = AuthService.login_user(user)
            
            return Response({
                'success': True,
                'message': '로그인 성공',
                'user': result['user'],
                'tokens': result['tokens']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'로그인 처리 중 오류가 발생했습니다: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': '로그인 실패',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    사용자 로그아웃 API
    POST /api/accounts/logout/
    """
    try:
        refresh_token = request.data.get('refresh')
        
        # 비즈니스 로직을 서비스로 위임
        result = AuthService.logout_user(refresh_token)
        
        return Response({
            'success': True,
            'message': result['message']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'로그아웃 실패: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh_view(request):
    """
    JWT 토큰 갱신 API
    POST /api/accounts/token/refresh/
    """
    serializer = TokenRefreshSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            refresh_token = serializer.validated_data['refresh']
            
            # 비즈니스 로직을 서비스로 위임
            result = AuthService.refresh_token(refresh_token)
            
            return Response({
                'success': True,
                'message': '토큰 갱신 성공',
                'tokens': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'토큰 갱신 실패: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': False,
        'message': '토큰 갱신 실패',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info_view(request):
    """
    현재 로그인된 사용자 정보 조회 API
    GET /api/accounts/user/
    """
    try:
        # 비즈니스 로직을 서비스로 위임
        user_data = UserService.get_user_info(request.user)
        
        return Response({
            'success': True,
            'user': user_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'사용자 정보 조회 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_profile_update_view(request):
    """
    사용자 프로필 수정 API
    PUT/PATCH /api/accounts/profile/
    """
    serializer = UserProfileUpdateSerializer(
        request.user, 
        data=request.data, 
        partial=(request.method == 'PATCH')
    )
    
    if serializer.is_valid():
        try:
            # 비즈니스 로직을 서비스로 위임
            result = UserService.update_user_profile(
                request.user, 
                serializer.validated_data
            )
            
            return Response({
                'success': True,
                'message': '프로필이 성공적으로 수정되었습니다.',
                'user': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'프로필 수정 실패: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': '프로필 수정 실패',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def password_change_view(request):
    """
    비밀번호 변경 API
    POST /api/accounts/password/change/
    """
    serializer = PasswordChangeSerializer(
        data=request.data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        try:
            # 비즈니스 로직을 서비스로 위임
            UserService.change_password(
                request.user,
                serializer.validated_data['current_password'],
                serializer.validated_data['new_password']
            )
            
            return Response({
                'success': True,
                'message': '비밀번호가 성공적으로 변경되었습니다.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'비밀번호 변경 실패: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': '비밀번호 변경 실패',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_user_id_view(request):
    """
    사용자 ID 중복 확인 API
    POST /api/accounts/check-user-id/
    """
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({
            'success': False,
            'message': '사용자 ID를 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 비즈니스 로직을 서비스로 위임
        is_available = UserService.is_user_id_available(user_id)
        
        return Response({
            'success': True,
            'available': is_available,
            'message': '사용 가능한 ID입니다.' if is_available else '이미 사용 중인 ID입니다.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'ID 확인 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    사용자 회원가입 API
    POST /api/accounts/register/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # 비즈니스 로직을 서비스로 위임
            result = AuthService.register_user(serializer.validated_data)
            
            return Response({
                'success': True,
                'message': '회원가입이 완료되었습니다.',
                'user': result['user'],
                'tokens': result['tokens']
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'회원가입 실패: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response({
        'success': False,
        'message': '회원가입 실패',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_list_view(request):
    """
    사용자 목록 조회 API (관리자용)
    GET /api/accounts/users/
    """
    # 관리자 권한 확인
    if not request.user.is_staff:
        return Response({
            'success': False,
            'message': '관리자 권한이 필요합니다.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # 비즈니스 로직을 서비스로 위임
        result = UserService.get_user_list_for_admin()
        
        return Response({
            'success': True,
            'users': result['users'],
            'count': result['count'],
            'statistics': result['statistics']
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'사용자 목록 조회 실패: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
