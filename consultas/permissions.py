from rest_framework import permissions


class EsPaciente(permissions.BasePermission):
    """Solo pacientes pueden acceder."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'paciente'


class EsPersonal(permissions.BasePermission):
    """Solo recepcionistas, doctores o admin pueden acceder."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['recepcionista', 'doctor', 'admin']


class EsDoctorOAdmin(permissions.BasePermission):
    """Solo doctores o admin."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ['doctor', 'admin']


class EsAdmin(permissions.BasePermission):
    """Solo admin."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == 'admin'


class EsPropietarioConsulta(permissions.BasePermission):
    """
    Permiso a nivel de objeto:
    - Un paciente solo puede ver SUS consultas.
    - Un doctor solo puede ver consultas asignadas a él.
    - Recepcionistas y admin ven todas.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if user.rol in ['recepcionista', 'admin']:
            return True
        
        if user.rol == 'paciente':
            return obj.paciente == user
        
        if user.rol == 'doctor':
            return obj.asignada_a == user
        
        return False