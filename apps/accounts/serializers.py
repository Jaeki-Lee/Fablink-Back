from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    userType = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'userType']
        
    def get_userType(self, obj):
        # 사용자 타입을 프로필 모델에서 가져오거나 그룹으로 판단
        if hasattr(obj, 'profile'):
            return obj.profile.user_type
        # 그룹으로 판단하는 경우
        if obj.groups.filter(name='designer').exists():
            return 'designer'
        elif obj.groups.filter(name='factory').exists():
            return 'factory'
        return None