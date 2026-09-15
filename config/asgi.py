"""
ASGI config for config project.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Inicializa Django antes de importar routing
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from consultas.middleware import JWTAuthMiddleware
from consultas.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    # HTTP requests (van a Django normal)
    'http': django_asgi_app,
    
    # WebSocket requests (van a Channels con JWT auth)
    'websocket': JWTAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})