import pytest
from django.core import mail
from django.utils import timezone
from datetime import timedelta

from consultas.models import Consulta
from consultas.tasks import enviar_reporte_semanal
from .factories import (
    AdminFactory, DoctorFactory, PacienteFactory,
    ConsultaFactory, MensajeFactory,
)


@pytest.mark.django_db
class TestEnviarReporteSemanal:
    def test_sin_admins_retorna_mensaje(self):
        """Si no hay admins con email, no envía nada."""
        resultado = enviar_reporte_semanal()
        assert 'No hay admins con email configurado' in resultado
    
    def test_envia_reporte_a_admins(self):
        """Envía el reporte a todos los admins con email."""
        AdminFactory(email='admin1@test.com', username='admin1')
        AdminFactory(email='admin2@test.com', username='admin2')
        
        resultado = enviar_reporte_semanal()
        
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert 'admin1@test.com' in email.to
        assert 'admin2@test.com' in email.to
        assert 'Reporte semanal' in email.subject
        assert 'REPORTE SEMANAL' in email.body
    
    def test_reporte_incluye_metricas(self):
        """El reporte incluye métricas correctas."""
        admin = AdminFactory(email='admin@test.com')
        doctor = DoctorFactory()
        
        hace_2_dias = timezone.now() - timedelta(days=2)
        paciente = PacienteFactory()
        
        c1 = ConsultaFactory(paciente=paciente, asignada_a=doctor)
        c2 = ConsultaFactory(paciente=paciente)
        
        # Fuerza fecha de creación en el modelo, no en la factory
        Consulta.objects.filter(id__in=[c1.id, c2.id]).update(creada=hace_2_dias)
        
        MensajeFactory(consulta=c1, autor=paciente)
        
        resultado = enviar_reporte_semanal()
        
        assert len(mail.outbox) == 1
        body = mail.outbox[0].body
        assert 'Consultas nuevas:' in body
        assert 'Mensajes intercambiados:' in body
        assert 'ACTIVIDAD POR DOCTOR' in body
    
    def test_sin_actividad_de_doctores(self):
        """Si no hay actividad de doctores, muestra el mensaje correcto."""
        AdminFactory(email='admin@test.com')
        
        resultado = enviar_reporte_semanal()
        
        assert 'Sin actividad registrada' in mail.outbox[0].body
    
    def test_retorna_cantidad_de_admins(self):
        """Retorna la cantidad de admins a los que se envió."""
        AdminFactory(email='admin1@test.com')
        AdminFactory(email='admin2@test.com')
        AdminFactory(email='')  # Sin email, no se cuenta
        
        resultado = enviar_reporte_semanal()
        
        assert 'Reporte enviado a 2 admin(s)' in resultado