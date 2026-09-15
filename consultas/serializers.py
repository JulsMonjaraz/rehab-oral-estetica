from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Consulta, Mensaje

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el usuario (datos públicos)."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'rol', 'telefono', 'especialidad', 'first_name', 'last_name']
        read_only_fields = ['id', 'rol']


class MensajeSerializer(serializers.ModelSerializer):
    """Serializer para mensajes del chat."""
    
    autor_nombre = serializers.CharField(source='autor.username', read_only=True)
    autor_rol = serializers.CharField(source='autor.rol', read_only=True)
    
    class Meta:
        model = Mensaje
        fields = ['id', 'consulta', 'autor', 'autor_nombre', 'autor_rol', 'contenido', 'leido', 'enviado']
        read_only_fields = ['id', 'autor', 'leido', 'enviado']


class ConsultaSerializer(serializers.ModelSerializer):
    """Serializer para consultas (con mensajes anidados)."""
    
    paciente_nombre = serializers.CharField(source='paciente.username', read_only=True)
    asignada_a_nombre = serializers.CharField(source='asignada_a.username', read_only=True)
    mensajes = MensajeSerializer(many=True, read_only=True)
    total_mensajes = serializers.SerializerMethodField()
    
    class Meta:
        model = Consulta
        fields = [
            'id', 'paciente', 'paciente_nombre', 'asignada_a', 'asignada_a_nombre',
            'motivo', 'descripcion', 'estado', 'prioridad',
            'creada', 'actualizada', 'mensajes', 'total_mensajes',
        ]
        read_only_fields = ['id', 'paciente', 'creada', 'actualizada']
    
    def get_total_mensajes(self, obj):
        return obj.mensajes.count()


class ConsultaListSerializer(serializers.ModelSerializer):
    """Serializer más ligero para listar consultas (sin mensajes)."""
    
    paciente_nombre = serializers.CharField(source='paciente.username', read_only=True)
    asignada_a_nombre = serializers.CharField(source='asignada_a.username', read_only=True)
    
    class Meta:
        model = Consulta
        fields = [
            'id', 'paciente_nombre', 'asignada_a_nombre',
            'motivo', 'estado', 'prioridad', 'creada', 'actualizada',
        ]
        read_only_fields = ['id', 'paciente_nombre', 'creada', 'actualizada']