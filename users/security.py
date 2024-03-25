from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from jwt import decode as jwt_decode
from rest_framework_simplejwt.settings import api_settings as jwt_settings

User = get_user_model()


def set_jwt_access_cookie(response, access_token):
    """
    Set the JWT access token as a cookie in the response

    Args:
        response (HttpResponse): The response object
        access_token (str): The JWT access token

    Returns:
        None
    """

    cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
    access_token_expiration = (timezone.now() + jwt_settings.ACCESS_TOKEN_LIFETIME)
    cookie_secure = getattr(settings, 'JWT_AUTH_SECURE', False)
    cookie_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', True)
    cookie_samesite = getattr(settings, 'JWT_AUTH_SAMESITE', 'Lax')

    if cookie_name:
        response.set_cookie(
            cookie_name,
            access_token,
            expires=access_token_expiration,
            secure=cookie_secure,
            httponly=cookie_httponly,
            samesite=cookie_samesite,
        )


def set_jwt_refresh_cookie(response, refresh_token):
    """
    Set the JWT refresh token as a cookie in the response

    Args:
        response (HttpResponse): The response object
        refresh_token (str): The JWT refresh token

    Returns:
        None
    """

    refresh_token_expiration = (timezone.now() + jwt_settings.REFRESH_TOKEN_LIFETIME)
    refresh_cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)
    refresh_cookie_path = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE_PATH', '/')
    cookie_secure = getattr(settings, 'JWT_AUTH_SECURE', False)
    cookie_httponly = getattr(settings, 'JWT_AUTH_HTTPONLY', True)
    cookie_samesite = getattr(settings, 'JWT_AUTH_SAMESITE', 'Lax')

    if refresh_cookie_name:
        response.set_cookie(
            refresh_cookie_name,
            refresh_token,
            expires=refresh_token_expiration,
            secure=cookie_secure,
            httponly=cookie_httponly,
            samesite=cookie_samesite,
            path=refresh_cookie_path,
        )


def unset_jwt_cookies(response):
    """
    Unset the JWT cookies in the response

    Args:
        response (HttpResponse): The response object

    Returns:
        None
    """

    cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
    refresh_cookie_name = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE', None)
    refresh_cookie_path = getattr(settings, 'JWT_AUTH_REFRESH_COOKIE_PATH', '/')
    cookie_samesite = getattr(settings, 'JWT_AUTH_SAMESITE', 'Lax')

    if cookie_name:
        response.delete_cookie(cookie_name, samesite=cookie_samesite)
    if refresh_cookie_name:
        response.delete_cookie(refresh_cookie_name, path=refresh_cookie_path, samesite=cookie_samesite)


def set_jwt_cookies(response, access_token, refresh_token):
    """
    Set the JWT cookies in the response

    Args:
        response (HttpResponse): The response object
        access_token (str): The JWT access token
        refresh_token (str): The JWT refresh token

    Returns:
        None
    """

    set_jwt_access_cookie(response, access_token)
    set_jwt_refresh_cookie(response, refresh_token)


@database_sync_to_async
def get_user(validated_token):
    try:
        user = get_user_model().objects.get(id=validated_token["user_id"])
        return user
    except User.DoesNotExist:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name.lower() == 'bearer':
                decoded_data = jwt_decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
                scope["user"] = await get_user(validated_token=decoded_data)
            else:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()
        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    return JwtAuthMiddleware(AuthMiddlewareStack(inner))
