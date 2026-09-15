from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Consulta, Mensaje
from .serializers import (
    UserSerializer, ConsultaSerializer, ConsultaListSerializer, MensajeSerializer,
)
from .permissions import EsPersonal, EsPropietarioConsulta
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint de solo lectura para el usuario actual."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Devuelve el usuario autenticado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ConsultaViewSet(viewsets.ModelViewSet):
    """
    CRUD de consultas.
    
    - Pacientes ven solo las suyas.
    - Doctores ven solo las asignadas a ellos.
    - Recepcionistas y admin ven todas.
    """
    
    permission_classes = [permissions.IsAuthenticated, EsPropietarioConsulta]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.rol in ['recepcionista', 'admin']:
            return Consulta.objects.all()
        
        if user.rol == 'paciente':
            return Consulta.objects.filter(paciente=user)
        
        if user.rol == 'doctor':
            return Consulta.objects.filter(asignada_a=user)
        
        return Consulta.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ConsultaListSerializer
        return ConsultaSerializer
    
    def perform_create(self, serializer):
        # El paciente es siempre el usuario autenticado
        serializer.save(paciente=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[EsPersonal])
    def asignar(self, request, pk=None):
        """Asigna un doctor a la consulta. Solo personal."""
        consulta = self.get_object()
        doctor_id = request.data.get('doctor_id')
        
        if not doctor_id:
            return Response(
                {'error': 'Se requiere doctor_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            doctor = User.objects.get(id=doctor_id, rol='doctor')
        except User.DoesNotExist:
            return Response(
                {'error': 'Doctor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        consulta.asignada_a = doctor
        consulta.estado = 'en_atencion'
        consulta.save()
        
        serializer = self.get_serializer(consulta)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[EsPersonal])
    def cerrar(self, request, pk=None):
        """Cierra una consulta."""
        consulta = self.get_object()
        consulta.estado = 'cerrada'
        consulta.save()
        serializer = self.get_serializer(consulta)
        return Response(serializer.data)


class MensajeViewSet(viewsets.ModelViewSet):
    """CRUD de mensajes. Cada usuario solo ve mensajes de sus consultas."""
    
    serializer_class = MensajeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        consulta_id = self.request.query_params.get('consulta')
        
        # Filtra por consulta si se pasa el query param
        if consulta_id:
            return Mensaje.objects.filter(consulta_id=consulta_id, consulta__in=self._consultas_visibles(user))
        
        return Mensaje.objects.filter(consulta__in=self._consultas_visibles(user))
    
    def _consultas_visibles(self, user):
        """Consulta reutilizable: consultas que el usuario puede ver."""
        if user.rol in ['recepcionista', 'admin']:
            return Consulta.objects.all()
        if user.rol == 'paciente':
            return Consulta.objects.filter(paciente=user)
        if user.rol == 'doctor':
            return Consulta.objects.filter(asignada_a=user)
        return Consulta.objects.none()
    
    def perform_create(self, serializer):
        consulta = serializer.validated_data['consulta']
        
        # Verifica que el usuario tenga acceso a esa consulta
        if consulta not in self._consultas_visibles(self.request.user):
            raise PermissionDenied('No tienes acceso a esta consulta.')
        
        serializer.save(autor=self.request.user)

@login_required
def chat_test_view(request, consulta_id):

    """Vista de prueba para el chat WebSocket."""
    consulta = get_object_or_404(Consulta, id=consulta_id)
    
    # Genera un token JWT para el usuario actual
    refresh = RefreshToken.for_user(request.user)
    
    return render(request, 'consultas/chat_test.html', {
        'consulta_id': consulta.id,
        'user': request.user,
        'token': str(refresh.access_token),
    })

@login_required
def notificaciones_test_view(request):
    """Vista de prueba para las notificaciones en tiempo real."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(request.user)
    return render(request, 'consultas/notificaciones_test.html', {
        'user': request.user,
        'token': str(refresh.access_token),
    })