from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class LoginSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, required=False)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        password = attrs.get('password')
        user_type = attrs.get('user_type')

        if user_id and password:
            user = authenticate(username=user_id, password=password)
            if user:
                if user_type and user.user_type != user_type:
                    raise serializers.ValidationError("선택한 사용자 타입과 계정 타입이 일치하지 않습니다.")
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("유저가 존재하지 않습니다. 아이디와 비밀번호를 확인해주세요.")
        else:
            raise serializers.ValidationError('사용자 ID와 비밀번호를 모두 입력해주세요.')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'name', 'user_type', 'contact', 'address', 'created_at']
        read_only_fields = ['id', 'created_at']

class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        if not attrs.get('refresh'):
            raise serializers.ValidationError('Refresh 토큰이 필요합니다.')
