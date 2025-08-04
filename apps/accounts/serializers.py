from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User

class LoginSerializer(serializers.Serializer):
    """통합 로그인 Serializer (Designer와 Factory 모두 지원)"""
    user_id = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=[('designer', '디자이너'), ('factory', '공장주')], required=True)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        password = attrs.get('password')
        user_type = attrs.get('user_type')

        if not user_id or not password:
            raise serializers.ValidationError('사용자 ID와 비밀번호를 모두 입력해주세요.')

        try:
            user = User.objects.get(user_id=user_id, user_type=user_type)
            
            if user.check_password(password):
                # 계정 활성화 상태 확인
                if not user.is_active:
                    raise serializers.ValidationError("비활성화된 계정입니다. 관리자에게 문의하세요.")
                
                attrs['user'] = user
                attrs['user_type'] = user_type
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
            attrs['refresh'] = str(refresh)
            return attrs
        except TokenError as e:
            raise serializers.ValidationError(f'유효하지 않은 토큰입니다: {str(e)}')


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 조회/수정 Serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'user_id', 'name', 'user_type', 'contact', 'address', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']