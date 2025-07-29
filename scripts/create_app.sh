#!/bin/bash
# scripts/create_app.sh

APP_NAME=$1
if [ -z "$APP_NAME" ]; then
    echo "Usage: $0 <app_name>"
    exit 1
fi

echo "🚀 새 앱 '$APP_NAME'을 생성합니다..."

# 앱 생성
python manage.py startapp $APP_NAME apps/$APP_NAME

# URL 파일 생성
cat > apps/$APP_NAME/j .py << EOF
from django.urls import path, include
from rest_framework.routers import DefaultRouter

app_name = '$APP_NAME'

router = DefaultRouter()
# router.register(r'items', ItemViewSet)  # 필요시 추가

urlpatterns = [
    path('', include(router.urls)),
]
EOF

# Serializer 파일 생성
touch apps/$APP_NAME/serializers.py

echo "✅ 앱 '$APP_NAME'이 생성되었습니다!"
echo "📝 다음 작업을 수행하세요:"
echo "   1. fablink_project/settings/base.py의 LOCAL_APPS에 'apps.$APP_NAME' 추가"
echo "   2. fablink_project/urls.py에 URL 패턴 추가"
echo "   3. 모델 작성 후 makemigrations 실행"
```