from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, required=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user_type = attrs.get('user_type')

        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                if user_type and user.user_type != user_type:
                    raise serializers.ValidationError("선택한 사용자 타입과 계정 타입이 일치하지 않습니다.")
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("아이디 또는 비밀번호가 잘못되었습니다.")
        else: 
            raise serializers.ValidationError("아이디와 비밀번호를 모두 입력해야 합니다.")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'date_joined']
        read_only_fields = ['id', 'date_joined']
