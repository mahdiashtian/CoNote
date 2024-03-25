from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from conote.consumers import OnlineUserConsumer
from users.security import JwtAuthMiddlewareStack

websocket_urlpatterns = [
    path("ws/online/", OnlineUserConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JwtAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
