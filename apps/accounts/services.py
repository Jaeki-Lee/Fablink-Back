"""
accounts 앱의 비즈니스 로직을 담당하는 서비스 레이어
"""

from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .serializers import UserSerializer, UserListSerializer


class AuthService:
    """
    인증 관련 비즈니스 로직을 처리하는 서비스
    """
    
    @staticmethod
    @transaction.atomic
    def register_user(user_data: dict) -> dict:
        """
        사용자 회원가입 처리
        
        Args:
            user_data (dict): 회원가입 데이터
            
        Returns:
            dict: 생성된 사용자 정보와 토큰
            
        Raises:
            serializers.ValidationError: 회원가입 실패 시
        """
        try:
            # 사용자 ID 중복 검사
            if User.objects.filter(user_id=user_data.get('user_id')).exists():
                raise serializers.ValidationError('이미 사용 중인 사용자 ID입니다.')
            
            # 비밀번호 분리
            password = user_data.pop('password', None)
            if not password:
                raise serializers.ValidationError('비밀번호가 필요합니다.')
            
            # 사용자 생성
            user = User.objects.create(**user_data)
            user.set_password(password)
            user.save()
            
            # 자동 로그인을 위한 토큰 생성
            tokens = AuthService.generate_tokens(user)
            
            return {
                'user': UserSerializer(user).data,
                'tokens': tokens
            }
            
        except Exception as e:
            raise serializers.ValidationError(f'회원가입 실패: {str(e)}')
    
    @staticmethod
    def login_user(user: User) -> dict:
        """
        사용자 로그인 처리
        
        Args:
            user (User): 로그인할 사용자 객체
            
        Returns:
            dict: 사용자 정보와 토큰
        """
        # 계정 활성화 상태 재확인
        if not user.is_active:
            raise serializers.ValidationError('비활성화된 계정입니다.')
        
        # 토큰 생성
        tokens = AuthService.generate_tokens(user)
        
        # 로그인 로그 기록 (필요시)
        AuthService._log_user_login(user)
        
        return {
            'user': UserSerializer(user).data,
            'tokens': tokens
        }
    
    @staticmethod
    def logout_user(refresh_token: str) -> dict:
        """
        사용자 로그아웃 처리
        
        Args:
            refresh_token (str): 블랙리스트에 추가할 토큰
            
        Returns:
            dict: 로그아웃 결과
            
        Raises:
            serializers.ValidationError: 로그아웃 실패 시
        """
        if not refresh_token:
            raise serializers.ValidationError('Refresh 토큰이 필요합니다.')
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return {'message': '로그아웃 성공'}
            
        except TokenError:
            raise serializers.ValidationError('유효하지 않은 토큰입니다.')
        except Exception as e:
            raise serializers.ValidationError(f'로그아웃 실패: {str(e)}')
    
    @staticmethod
    def authenticate_user(user_id: str, password: str) -> User:
        """
        사용자 인증 처리
        
        Args:
            user_id (str): 사용자 ID
            password (str): 비밀번호
            
        Returns:
            User: 인증된 사용자 객체
            
        Raises:
            serializers.ValidationError: 인증 실패 시
        """
        if not user_id or not password:
            raise serializers.ValidationError('사용자 ID와 비밀번호를 모두 입력해주세요.')
        
        try:
            user = User.objects.get(user_id=user_id)
            if user.check_password(password):
                if not user.is_active:
                    raise serializers.ValidationError('비활성화된 계정입니다. 관리자에게 문의하세요.')
                return user
            else:
                raise serializers.ValidationError('비밀번호가 올바르지 않습니다.')
        except User.DoesNotExist:
            raise serializers.ValidationError('존재하지 않는 사용자입니다.')
    
    @staticmethod
    def generate_tokens(user: User) -> dict:
        """
        JWT 토큰 생성
        
        Args:
            user (User): 토큰을 생성할 사용자
            
        Returns:
            dict: access, refresh 토큰
        """
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
    
    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        """
        토큰 갱신 처리
        
        Args:
            refresh_token (str): 리프레시 토큰
            
        Returns:
            dict: 새로운 토큰들
            
        Raises:
            serializers.ValidationError: 토큰 갱신 실패 시
        """
        if not refresh_token:
            raise serializers.ValidationError('Refresh 토큰이 필요합니다.')
        
        try:
            refresh = RefreshToken(refresh_token)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        except TokenError as e:
            raise serializers.ValidationError(f'유효하지 않은 토큰입니다: {str(e)}')
    
    @staticmethod
    def _log_user_login(user: User):
        """
        사용자 로그인 로그 기록 (내부 메서드)
        
        Args:
            user (User): 로그인한 사용자
        """
        # 로그인 시간 업데이트
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # 필요시 로그인 히스토리 테이블에 기록
        # LoginHistory.objects.create(user=user, login_time=timezone.now())


class UserService:
    """
    사용자 관리 관련 비즈니스 로직을 처리하는 서비스
    """
    
    @staticmethod
    def get_user_info(user: User) -> dict:
        """
        사용자 정보 조회
        
        Args:
            user (User): 조회할 사용자
            
        Returns:
            dict: 사용자 정보
        """
        return UserSerializer(user).data
    
    @staticmethod
    @transaction.atomic
    def create_user(user_data: dict) -> User:
        """
        새 사용자 생성
        
        Args:
            user_data (dict): 사용자 데이터
            
        Returns:
            User: 생성된 사용자
            
        Raises:
            serializers.ValidationError: 사용자 생성 실패 시
        """
        try:
            # 사용자 ID 중복 검사
            if User.objects.filter(user_id=user_data.get('user_id')).exists():
                raise serializers.ValidationError('이미 사용 중인 사용자 ID입니다.')
            
            # 비밀번호 분리
            password = user_data.pop('password', None)
            if not password:
                raise serializers.ValidationError('비밀번호가 필요합니다.')
            
            # 사용자 생성
            user = User.objects.create(**user_data)
            user.set_password(password)
            user.save()
            
            return user
            
        except Exception as e:
            raise serializers.ValidationError(f'사용자 생성 실패: {str(e)}')
    
    @staticmethod
    @transaction.atomic
    def update_user_profile(user: User, update_data: dict) -> dict:
        """
        사용자 프로필 업데이트
        
        Args:
            user (User): 업데이트할 사용자
            update_data (dict): 업데이트 데이터
            
        Returns:
            dict: 업데이트된 사용자 정보
        """
        allowed_fields = ['name', 'contact', 'address']
        
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        user.save()
        
        # 업데이트된 사용자 정보 반환
        return UserSerializer(user).data
    
    @staticmethod
    @transaction.atomic
    def change_password(user: User, current_password: str, new_password: str) -> bool:
        """
        사용자 비밀번호 변경
        
        Args:
            user (User): 비밀번호를 변경할 사용자
            current_password (str): 현재 비밀번호
            new_password (str): 새 비밀번호
            
        Returns:
            bool: 변경 성공 여부
            
        Raises:
            serializers.ValidationError: 비밀번호 변경 실패 시
        """
        if not user.check_password(current_password):
            raise serializers.ValidationError('현재 비밀번호가 올바르지 않습니다.')
        
        user.set_password(new_password)
        user.save()
        
        # 비밀번호 변경 후 모든 토큰 무효화 (보안)
        UserService._invalidate_all_user_tokens(user)
        
        return True
    
    @staticmethod
    def get_user_by_id(user_id: str) -> User:
        """
        사용자 ID로 사용자 조회
        
        Args:
            user_id (str): 조회할 사용자 ID
            
        Returns:
            User: 조회된 사용자
            
        Raises:
            User.DoesNotExist: 사용자가 존재하지 않을 때
        """
        return User.objects.get(user_id=user_id)
    
    @staticmethod
    def get_users_by_type(user_type: str) -> list:
        """
        사용자 타입별 사용자 목록 조회
        
        Args:
            user_type (str): 사용자 타입
            
        Returns:
            list: 사용자 목록
        """
        return User.objects.filter(user_type=user_type, is_active=True)
    
    @staticmethod
    def get_all_users() -> list:
        """
        모든 사용자 목록 조회 (관리자용)
        
        Returns:
            list: 모든 사용자 목록
        """
        return User.objects.all().order_by('-created_at')
    
    @staticmethod
    def get_user_list_for_admin() -> dict:
        """
        관리자용 사용자 목록과 통계 조회
        
        Returns:
            dict: 사용자 목록, 개수, 통계 정보
        """
        users = User.objects.all().order_by('-created_at')
        serializer = UserListSerializer(users, many=True)
        statistics = UserService.get_user_statistics()
        
        return {
            'users': serializer.data,
            'count': len(serializer.data),
            'statistics': statistics
        }
    
    @staticmethod
    def is_user_id_available(user_id: str) -> bool:
        """
        사용자 ID 사용 가능 여부 확인
        
        Args:
            user_id (str): 확인할 사용자 ID
            
        Returns:
            bool: 사용 가능 여부 (True: 사용 가능, False: 이미 사용 중)
        """
        return not User.objects.filter(user_id=user_id).exists()
    
    @staticmethod
    def activate_user(user_id: str) -> User:
        """
        사용자 계정 활성화
        
        Args:
            user_id (str): 활성화할 사용자 ID
            
        Returns:
            User: 활성화된 사용자
        """
        user = User.objects.get(user_id=user_id)
        user.is_active = True
        user.save()
        return user
    
    @staticmethod
    def deactivate_user(user_id: str) -> User:
        """
        사용자 계정 비활성화
        
        Args:
            user_id (str): 비활성화할 사용자 ID
            
        Returns:
            User: 비활성화된 사용자
        """
        user = User.objects.get(user_id=user_id)
        user.is_active = False
        user.save()
        
        # 계정 비활성화 시 모든 토큰 무효화
        UserService._invalidate_all_user_tokens(user)
        
        return user
    
    @staticmethod
    def get_user_statistics() -> dict:
        """
        사용자 통계 정보 조회
        
        Returns:
            dict: 사용자 통계 정보
        """
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        
        user_type_stats = {}
        for choice in User.USER_TYPE_CHOICES:
            user_type = choice[0]
            count = User.objects.filter(user_type=user_type).count()
            user_type_stats[user_type] = count
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'user_type_distribution': user_type_stats
        }
    
    @staticmethod
    def _invalidate_all_user_tokens(user: User):
        """
        사용자의 모든 토큰 무효화 (내부 메서드)
        
        Args:
            user (User): 토큰을 무효화할 사용자
        """
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
        
        # 해당 사용자의 모든 outstanding 토큰을 블랙리스트에 추가
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            try:
                refresh_token = RefreshToken(token.token)
                refresh_token.blacklist()
            except TokenError:
                # 이미 만료된 토큰은 무시
                pass


# timezone import 추가
from django.utils import timezone
