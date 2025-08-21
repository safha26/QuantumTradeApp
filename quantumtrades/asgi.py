import os

from channels.routing import ProtocolTypeRouter, URLRouter

from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack

import trade.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quantumtrades.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            trade.routing.websocket_urlpatterns
        )
    ),
})
