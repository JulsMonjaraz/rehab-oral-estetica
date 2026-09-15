from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

User = get_user_model()


@shared_task
def enviar_reporte_semanal():
    """Envía un reporte semanal al admin con métricas de la clínica."""
    from .models import Consulta, Mensaje
    
    hoy = timezone.now()
    hace_7_dias = hoy - timedelta(days=7)
    
    # Métricas
    consultas_nuevas = Consulta.objects.filter(creada__gte=hace_7_dias).count()
    consultas_cerradas = Consulta.objects.filter(
        estado='cerrada',
        actualizada__gte=hace_7_dias,
    ).count()
    consultas_urgentes = Consulta.objects.filter(
        prioridad__in=['urgente', 'dolor_agudo'],
        creada__gte=hace_7_dias,
    ).count()
    mensajes_totales = Mensaje.objects.filter(enviado__gte=hace_7_dias).count()
    
    # Consultas por estado (todas las abiertas)
    pendientes = Consulta.objects.filter(estado='pendiente').count()
    en_atencion = Consulta.objects.filter(estado='en_atencion').count()
    en_tratamiento = Consulta.objects.filter(estado='tratamiento').count()
    
    # Doctores más activos
    doctores = User.objects.filter(rol='doctor')
    doctores_metricas = []
    for doctor in doctores:
        asignadas = Consulta.objects.filter(
            asignada_a=doctor,
            actualizada__gte=hace_7_dias,
        ).count()
        if asignadas > 0:
            doctores_metricas.append(f'  - Dr. {doctor.username}: {asignadas} consultas')
    
    # Construye el reporte
    reporte = f'''
📊 REPORTE SEMANAL — Rehab Oral y Estética
Semana del {hace_7_dias.date().strftime('%d/%m/%Y')} al {hoy.date().strftime('%d/%m/%Y')}

════════════════════════════════════════
📈 ACTIVIDAD DE LA SEMANA
════════════════════════════════════════
  • Consultas nuevas: {consultas_nuevas}
  • Consultas cerradas: {consultas_cerradas}
  • Consultas urgentes: {consultas_urgentes}
  • Mensajes intercambiados: {mensajes_totales}

════════════════════════════════════════
🔄 ESTADO ACTUAL DEL SISTEMA
════════════════════════════════════════
  • Pendientes: {pendientes}
  • En atención: {en_atencion}
  • En tratamiento: {en_tratamiento}

════════════════════════════════════════
👨‍⚕️ ACTIVIDAD POR DOCTOR
════════════════════════════════════════
{chr(10).join(doctores_metricas) if doctores_metricas else '  (Sin actividad registrada)'}

════════════════════════════════════════
Este es un reporte automático generado por Rehab Oral y Estética.
Para ver más detalles, ingresa al panel de administración.
    '''
    
    # Envía a todos los admins
    admins = User.objects.filter(rol='admin')
    emails = [a.email for a in admins if a.email]
    
    if not emails:
        return 'No hay admins con email configurado'
    
    send_mail(
        subject=f'📊 Reporte semanal — {hoy.date().strftime("%d/%m/%Y")}',
        message=reporte,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=emails,
        fail_silently=False,
    )
    
    return f'Reporte enviado a {len(emails)} admin(s)'