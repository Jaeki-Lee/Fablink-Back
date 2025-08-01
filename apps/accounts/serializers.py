from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import Designer, Factory

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

        user = None
        
        # 사용자 타입에 따라 다른 모델에서 검색
        try:
            if user_type == 'designer':
                user = Designer.objects.get(user_id=user_id)
            elif user_type == 'factory':
                user = Factory.objects.get(user_id=user_id)
            else:
                raise serializers.ValidationError("올바른 사용자 타입을 선택해주세요.")
            
            if user.check_password(password):
                # 계정 활성화 상태 확인
                if not user.is_active:
                    raise serializers.ValidationError("비활성화된 계정입니다. 관리자에게 문의하세요.")
                
                attrs['user'] = user
                attrs['user_type'] = user_type
                return attrs
            else:
                raise serializers.ValidationError("비밀번호가 올바르지 않습니다.")
                
        except (Designer.DoesNotExist, Factory.DoesNotExist):
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


class DesignerSerializer(serializers.ModelSerializer):
    """디자이너 정보 조회/수정 Serializer"""
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Designer
        fields = ['id', 'user_id', 'name', 'contact', 'address', 'profile_image', 'profile_image_url', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']
    
    def get_profile_image_url(self, obj):
        """프로필 이미지 URL 반환"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None


class FactorySerializer(serializers.ModelSerializer):
    """공장주 정보 조회/수정 Serializer"""
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Factory
        fields = ['id', 'user_id', 'name', 'company_name', 'business_license', 'contact', 'address', 
                 'profile_image', 'profile_image_url', 'production_capacity', 'specialties', 
                 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']
    
    def get_profile_image_url(self, obj):
        """프로필 이미지 URL 반환"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
