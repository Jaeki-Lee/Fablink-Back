from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """사용자 회원가입 Serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'name', 'user_type', 'contact', 'address', 'password', 'password_confirm']
        extra_kwargs = {
            'user_id': {'required': True},
            'name': {'required': True},
            'user_type': {'required': True},
        }
    
    def validate_user_id(self, value):
        """사용자 ID 중복 검사"""
        if User.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("이미 사용 중인 사용자 ID입니다.")
        return value
    
    def validate(self, attrs):
        """비밀번호 확인 검증"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        if password != password_confirm:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        
        return attrs
    
    def create(self, validated_data):
        """사용자 생성 - 비밀번호 해싱 처리"""
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)  # 비밀번호 해싱
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """로그인 Serializer"""
    user_id = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, required=False)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        password = attrs.get('password')
        user_type = attrs.get('user_type')

        if not user_id or not password:
            raise serializers.ValidationError('사용자 ID와 비밀번호를 모두 입력해주세요.')

        # 커스텀 User 모델에 맞게 인증 방식 수정
        try:
            user = User.objects.get(user_id=user_id)
            if user.check_password(password):
                # 사용자 타입 검증 (선택사항)
                if user_type and user.user_type != user_type:
                    raise serializers.ValidationError("선택한 사용자 타입과 계정 타입이 일치하지 않습니다.")
                
                # 계정 활성화 상태 확인
                if not user.is_active:
                    raise serializers.ValidationError("비활성화된 계정입니다. 관리자에게 문의하세요.")
                
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("비밀번호가 올바르지 않습니다.")
        except User.DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")


class TokenRefreshSerializer(serializers.Serializer):
    """JWT 토큰 갱신 Serializer"""
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh')
        
        if not refresh_token:
            raise serializers.ValidationError('Refresh 토큰이 필요합니다.')
        
        try:
            # 토큰 유효성 검사 및 새 액세스 토큰 생성
            refresh = RefreshToken(refresh_token)
            attrs['access'] = str(refresh.access_token)
            attrs['refresh'] = str(refresh)  # 새로운 refresh 토큰도 생성
            return attrs
        except TokenError as e:
            raise serializers.ValidationError(f'유효하지 않은 토큰입니다: {str(e)}')


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 조회/수정 Serializer"""
    class Meta:
        model = User
        fields = ['id', 'user_id', 'name', 'user_type', 'contact', 'address', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'user_type', 'created_at', 'updated_at']  # user_id와 user_type은 수정 불가


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """사용자 프로필 수정 전용 Serializer"""
    class Meta:
        model = User
        fields = ['name', 'contact', 'address']
        
    def validate_contact(self, value):
        """연락처 형식 검증"""
        import re
        if value and not re.match(r'^010-\d{4}-\d{4}$', value):
            raise serializers.ValidationError("연락처는 010-0000-0000 형식으로 입력해주세요.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """비밀번호 변경 Serializer"""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """현재 비밀번호 확인"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("현재 비밀번호가 올바르지 않습니다.")
        return value
    
    def validate(self, attrs):
        """새 비밀번호 확인"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError("새 비밀번호가 일치하지 않습니다.")
        
        return attrs
    
    def save(self):
        """비밀번호 변경 실행"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    """사용자 목록 조회용 간단한 Serializer (관리자용)"""
    class Meta:
        model = User
        fields = ['id', 'user_id', 'name', 'user_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'user_id', 'name', 'user_type', 'is_active', 'created_at']
