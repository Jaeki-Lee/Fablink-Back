from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .services import AuthService, UserService

User = get_user_model()


class AuthServiceTest(TestCase):
    """
    AuthService 테스트
    """
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.user_data = {
            'user_id': 'testuser',
            'password': 'testpass123',
            'name': '테스트 사용자',
            'user_type': 'designer'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_login_user_success(self):
        """로그인 성공 테스트"""
        result = AuthService.login_user(
            user_id=self.user_data['user_id'],
            password=self.user_data['password']
        )
        
        self.assertEqual(result['user'], self.user)
        self.assertIsInstance(result['token'], Token)
        self.assertIn('is_new_token', result)
    
    def test_login_user_invalid_credentials(self):
        """잘못된 인증 정보로 로그인 테스트"""
        with self.assertRaises(serializers.ValidationError):
            AuthService.login_user(
                user_id=self.user_data['user_id'],
                password='wrongpassword'
            )
    
    def test_login_user_wrong_user_type(self):
        """잘못된 사용자 타입으로 로그인 테스트"""
        with self.assertRaises(serializers.ValidationError):
            AuthService.login_user(
                user_id=self.user_data['user_id'],
                password=self.user_data['password'],
                user_type='manufacturer'  # 실제는 designer
            )
    
    def test_login_user_empty_credentials(self):
        """빈 인증 정보로 로그인 테스트"""
        with self.assertRaises(serializers.ValidationError):
            AuthService.login_user(user_id='', password='')
    
    def test_logout_user_success(self):
        """로그아웃 성공 테스트"""
        # 먼저 토큰 생성
        token = Token.objects.create(user=self.user)
        
        result = AuthService.logout_user(self.user)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], '로그아웃 성공')
        
        # 토큰이 삭제되었는지 확인
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=self.user)
    
    def test_logout_user_no_token(self):
        """토큰이 없는 상태에서 로그아웃 테스트"""
        with self.assertRaises(serializers.ValidationError):
            AuthService.logout_user(self.user)
    
    def test_get_user_info(self):
        """사용자 정보 조회 테스트"""
        user_info = AuthService.get_user_info(self.user)
        
        self.assertEqual(user_info['user_id'], self.user_data['user_id'])
        self.assertEqual(user_info['name'], self.user_data['name'])
        self.assertEqual(user_info['user_type'], self.user_data['user_type'])


class UserServiceTest(TestCase):
    """
    UserService 테스트
    """
    
    def setUp(self):
        """테스트 데이터 설정"""
        self.user_data = {
            'user_id': 'testuser',
            'password': 'testpass123',
            'name': '테스트 사용자',
            'user_type': 'designer',
            'contact': '010-1234-5678',
            'address': '서울시 강남구'
        }
    
    def test_create_user(self):
        """사용자 생성 테스트"""
        user = UserService.create_user(self.user_data)
        
        self.assertEqual(user.user_id, self.user_data['user_id'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertEqual(user.user_type, self.user_data['user_type'])
        self.assertTrue(user.check_password(self.user_data['password']))
    
    def test_update_user(self):
        """사용자 정보 업데이트 테스트"""
        user = User.objects.create_user(**self.user_data)
        
        update_data = {
            'name': '수정된 이름',
            'contact': '010-9876-5432'
        }
        
        updated_user = UserService.update_user(user, update_data)
        
        self.assertEqual(updated_user.name, update_data['name'])
        self.assertEqual(updated_user.contact, update_data['contact'])
    
    def test_get_users_by_type(self):
        """사용자 타입별 조회 테스트"""
        # 디자이너 사용자 생성
        User.objects.create_user(**self.user_data)
        
        # 제조업체 사용자 생성
        manufacturer_data = self.user_data.copy()
        manufacturer_data['user_id'] = 'manufacturer1'
        manufacturer_data['user_type'] = 'manufacturer'
        User.objects.create_user(**manufacturer_data)
        
        designers = UserService.get_users_by_type('designer')
        manufacturers = UserService.get_users_by_type('manufacturer')
        
        self.assertEqual(len(designers), 1)
        self.assertEqual(len(manufacturers), 1)
        self.assertEqual(designers[0].user_type, 'designer')
        self.assertEqual(manufacturers[0].user_type, 'manufacturer')
    
    def test_is_user_id_available(self):
        """사용자 ID 사용 가능 여부 테스트"""
        # 사용자 생성 전
        self.assertTrue(UserService.is_user_id_available('newuser'))
        
        # 사용자 생성
        User.objects.create_user(**self.user_data)
        
        # 사용자 생성 후
        self.assertFalse(UserService.is_user_id_available(self.user_data['user_id']))
        self.assertTrue(UserService.is_user_id_available('anotheruser'))
