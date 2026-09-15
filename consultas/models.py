from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Usuario personalizado con roles del sistema."""
    
    ROL_CHOICES = [
        ('paciente', 'Paciente'),
        ('recepcionista', 'Recepcionista'),
        ('doctor', 'Doctor'),
        ('admin', 'Administrador'),
    ]
    
    ESPECIALIDAD_CHOICES = [
        ('rehabilitacion', 'Rehabilitación Oral'),
        ('estetica', 'Odontología Estética'),
        ('implantologia', 'Implantología'),
        ('general', 'Odontología General'),
        ('otra', 'Otra'),
    ]
    
    rol = models.CharField('Rol', max_length=20, choices=ROL_CHOICES, default='paciente')
    telefono = models.CharField('Teléfono', max_length=20, blank=True, null=True)
    especialidad = models.CharField(
        'Especialidad',
        max_length=30,
        choices=ESPECIALIDAD_CHOICES,
        blank=True,
        null=True,
        help_text='Solo aplica para doctores',
    )
    
    def __str__(self):
        return f'{self.username} ({self.get_rol_display()})'
    
    @property
    def es_personal(self):
        """True si es recepcionista, doctor o admin."""
        return self.rol in ['recepcionista', 'doctor', 'admin']


class Consulta(models.Model):
    """Consulta de un paciente. Puede ser una duda, urgencia o solicitud de cita."""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_atencion', 'En atención'),
        ('tratamiento', 'En tratamiento'),
        ('cerrada', 'Cerrada'),
    ]
    
    PRIORIDAD_CHOICES = [
        ('normal', 'Normal'),
        ('urgente', 'Urgente'),
        ('dolor_agudo', 'Dolor agudo'),
    ]
    
    paciente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='consultas_como_paciente',
    )
    asignada_a = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultas_asignadas',
        help_text='Doctor o recepcionista asignado',
    )
    motivo = models.CharField('Motivo', max_length=200)
    descripcion = models.TextField('Descripción', blank=True, null=True)
    estado = models.CharField('Estado', max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField('Prioridad', max_length=20, choices=PRIORIDAD_CHOICES, default='normal')
    
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-actualizada']
    
    def __str__(self):
        return f'#{self.id} — {self.motivo} ({self.paciente.username})'
    
    @property
    def esta_abierta(self):
        return self.estado != 'cerrada'


class Mensaje(models.Model):
    """Mensaje dentro de una consulta (chat)."""
    
    consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='mensajes')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField('Contenido')
    leido = models.BooleanField(default=False)
    enviado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['enviado']
    
    def __str__(self):
        return f'{self.autor.username}: {self.contenido[:40]}'