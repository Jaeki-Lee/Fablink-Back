"""
accounts 앱의 비즈니스 로직을 담당하는 서비스 레이어
"""

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from .models import User
from .serializers import UserSerializer


class AuthService:
    """
    인증 관련 비즈니스 로직을 처리하는 서비스
    """
    
    @staticmethod
    def login_user(user_id: str, password: str, user_type: str = None) -> dict:
        """
        사용자 로그인 처리
        
        Args:
            user_id (str): 사용자 ID
            password (str): 비밀번호
            user_type (str, optional): 사용자 타입
            
        Returns:
            dict: 로그인 결과 (user, token)
            
        Raises:
            serializers.ValidationError: 로그인 실패 시
        """
        if not user_id or not password:
            raise serializers.ValidationError('사용자 ID와 비밀번호를 모두 입력해주세요.')
        
        # 사용자 인증
        user = authenticate(username=user_id, password=password)
        if not user:
            raise serializers.ValidationError("유저가 존재하지 않습니다. 아이디와 비밀번호를 확인해주세요.")
        
        # 사용자 타입 검증
        if user_type and user.user_type != user_type:
            raise serializers.ValidationError("선택한 사용자 타입과 계정 타입이 일치하지 않습니다.")
        
        # 토큰 생성 또는 조회
        token, created = Token.objects.get_or_create(user=user)
        
        return {
            'user': user,
            'token': token,
            'is_new_token': created
        }
    
    @staticmethod
    def logout_user(user: User) -> dict:
        """
        사용자 로그아웃 처리
        
        Args:
            user (User): 로그아웃할 사용자
            
        Returns:
            dict: 로그아웃 결과
            
        Raises:
            serializers.ValidationError: 로그아웃 실패 시
        """
        try:
            user.auth_token.delete()
            return {'success': True, 'message': '로그아웃 성공'}
        except Token.DoesNotExist:
            raise serializers.ValidationError('이미 로그아웃되었습니다.')
        except Exception as e:
            raise serializers.ValidationError(f'로그아웃 실패: {str(e)}')
    
    @staticmethod
    def get_user_info(user: User) -> dict:
        """
        사용자 정보 조회
        
        Args:
            user (User): 조회할 사용자
            
        Returns:
            dict: 사용자 정보
        """
        serializer = UserSerializer(user)
        return serializer.data


class UserService:
    """
    사용자 관리 관련 비즈니스 로직을 처리하는 서비스
    """
    
    @staticmethod
    def create_user(user_data: dict) -> User:
        """
        새 사용자 생성
        
        Args:
            user_data (dict): 사용자 데이터
            
        Returns:
            User: 생성된 사용자
        """
        # 사용자 생성 로직
        user = User.objects.create_user(**user_data)
        return user
    
    @staticmethod
    def update_user(user: User, update_data: dict) -> User:
        """
        사용자 정보 업데이트
        
        Args:
            user (User): 업데이트할 사용자
            update_data (dict): 업데이트 데이터
            
        Returns:
            User: 업데이트된 사용자
        """
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.save()
        return user
    
    @staticmethod
    def get_users_by_type(user_type: str) -> list:
        """
        사용자 타입별 사용자 목록 조회
        
        Args:
            user_type (str): 사용자 타입
            
        Returns:
            list: 사용자 목록
        """
        return User.objects.filter(user_type=user_type)
    
    @staticmethod
    def is_user_id_available(user_id: str) -> bool:
        """
        사용자 ID 사용 가능 여부 확인
        
        Args:
            user_id (str): 확인할 사용자 ID
            
        Returns:
            bool: 사용 가능 여부
        """
        return not User.objects.filter(user_id=user_id).exists()
