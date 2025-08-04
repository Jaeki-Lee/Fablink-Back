import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        logger.info(f"CustomJWTAuthentication.get_header called for path: {request.path}")
        header = super().get_header(request)
        if header:
            logger.info(f"Authorization header found: {header.decode('utf-8')[:50]}...")
        else:
            logger.info("Authorization header not found")
        return header
