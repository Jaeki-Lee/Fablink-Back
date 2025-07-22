from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class LoginSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=30)
    user_password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, required=False)

    def validate(self, data):
        user_id = data.get('user_id')
        user_password = data.get('user_password')
        user_type = data.get('user_type')

        if user_id and user_password:
            user = authenticate(username=user_id, password=user_password)
            
            if user:
                if  user.user_type != user_type:
                    raise serializers.ValidationError("선택한 사용자 타입과 계정 타입이 일치하지 않습니다.")
                data['user'] = user
                return user
            else:
                raise serializers.ValidationError("아이디 또는 비밀번호가 잘못되었습니다.")
        
        else: 
            raise serializers.ValidationError("아이디와 비밀번호를 모두 입력해야 합니다.")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'phone', 'company', 'date_joined']
        read_only_fields = ['id', 'date_joined']