from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from .tokens import DesignerToken, FactoryToken
from .models import Designer, Factory


class DesignerAuthentication(BaseAuthentication):
    """Designer용 JWT 인증"""
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = DesignerToken.verify_token(token)
            
            if payload.get('user_type') != 'designer':
                return None
                
            designer = Designer.objects.get(id=payload['designer_id'])
            
            # AnonymousUser 대신 Designer 객체를 user로 사용
            return (designer, token)
            
        except Designer.DoesNotExist:
            raise AuthenticationFailed('Designer not found')
        except Exception as e:
            raise AuthenticationFailed(str(e))


class FactoryAuthentication(BaseAuthentication):
    """Factory용 JWT 인증"""
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = FactoryToken.verify_token(token)
            
            if payload.get('user_type') != 'factory':
                return None
                
            factory = Factory.objects.get(id=payload['factory_id'])
            
            # AnonymousUser 대신 Factory 객체를 user로 사용
            return (factory, token)
            
        except Factory.DoesNotExist:
            raise AuthenticationFailed('Factory not found')
        except Exception as e:
            raise AuthenticationFailed(str(e))