import logging
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings

logger = logging.getLogger(__name__)

class CustomJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        logger.info(f"CustomJWTAuthentication.get_header called for path: {request.path}")
        header = super().get_header(request)
        if header is None:
            logger.info("Authorization header not found, checking cookies...")
            # Try to get the token from a cookie
            raw_token = request.COOKIES.get('authToken')
            if raw_token:
                logger.info(f"authToken cookie found: {raw_token[:10]}...") # Log first 10 chars for security
                return f'{api_settings.AUTH_HEADER_TYPES[0]} {raw_token}'.encode('utf-8')
            else:
                logger.info("authToken cookie not found.")
        else:
            logger.info(f"Authorization header found: {header.decode('utf-8')[:50]}...") # Log first 50 chars for security
        return header
