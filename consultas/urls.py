from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ConsultaViewSet, MensajeViewSet,
    chat_test_view, notificaciones_test_view,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'consultas', ConsultaViewSet, basename='consulta')
router.register(r'mensajes', MensajeViewSet, basename='mensaje')

urlpatterns = [
    path('chat/<int:consulta_id>/', chat_test_view, name='chat_test'),
    path('notificaciones/', notificaciones_test_view, name='notificaciones_test'),
    path('', include(router.urls)),
]