from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Consulta, Mensaje


@receiver(post_save, sender=Consulta)
def notificar_nueva_consulta(sender, instance, created, **kwargs):
    print(f"[SIGNAL DEBUG] post_save Consulta: created={created}, id={instance.id}")
    if not created:
        return
    
    channel_layer = get_channel_layer()
    print(f"[SIGNAL DEBUG] channel_layer: {channel_layer}")
    
    async_to_sync(channel_layer.group_send)(
        'notificaciones_staff',
        {
            'type': 'nueva_consulta',
            'consulta_id': instance.id,
            'paciente': instance.paciente.username,
            'motivo': instance.motivo,
            'prioridad': instance.prioridad,
        }
    )
    print("[SIGNAL DEBUG] Notificación nueva consulta enviada")


@receiver(post_save, sender=Mensaje)
def notificar_nuevo_mensaje(sender, instance, created, **kwargs):
    print(f"[SIGNAL DEBUG] post_save Mensaje: created={created}, id={instance.id}, autor_rol={instance.autor.rol}")
    if not created:
        return
    
    channel_layer = get_channel_layer()
    consulta = instance.consulta
    
    if instance.autor.rol == 'paciente':
        print("[SIGNAL DEBUG] Enviando notificación a notificaciones_staff")
        async_to_sync(channel_layer.group_send)(
            'notificaciones_staff',
            {
                'type': 'nuevo_mensaje',
                'consulta_id': consulta.id,
                'autor': instance.autor.username,
                'contenido': instance.contenido,
            }
        )
        print("[SIGNAL DEBUG] Notificación nuevo mensaje enviada")
    else:
        print("[SIGNAL DEBUG] Autor NO es paciente, no se envía")