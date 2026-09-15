import pytest
from consultas.models import User, Consulta, Mensaje
from .factories import (
    PacienteFactory, DoctorFactory, RecepcionistaFactory,
    AdminFactory, ConsultaFactory, MensajeFactory,
)


@pytest.mark.django_db
class TestUserModel:
    def test_es_personal_paciente(self):
        paciente = PacienteFactory()
        assert paciente.es_personal is False
    
    def test_es_personal_recepcionista(self):
        recep = RecepcionistaFactory()
        assert recep.es_personal is True
    
    def test_es_personal_doctor(self):
        doctor = DoctorFactory()
        assert doctor.es_personal is True
    
    def test_es_personal_admin(self):
        admin = AdminFactory()
        assert admin.es_personal is True
    
    def test_str_incluye_rol(self):
        paciente = PacienteFactory(rol='paciente')
        assert 'Paciente' in str(paciente)


@pytest.mark.django_db
class TestConsultaModel:
    def test_esta_abierta_si_no_cerrada(self):
        consulta = ConsultaFactory(estado='pendiente')
        assert consulta.esta_abierta is True
    
    def test_no_esta_abierta_si_cerrada(self):
        consulta = ConsultaFactory(estado='cerrada')
        assert consulta.esta_abierta is False
    
    def test_str_incluye_motivo_y_paciente(self):
        consulta = ConsultaFactory(motivo='Dolor de muela')
        assert 'Dolor de muela' in str(consulta)


@pytest.mark.django_db
class TestMensajeModel:
    def test_mensaje_se_crea_con_autor(self):
        mensaje = MensajeFactory(contenido='Hola')
        assert mensaje.contenido == 'Hola'
        assert mensaje.autor is not None
    
    def test_mensaje_por_defecto_no_leido(self):
        mensaje = MensajeFactory()
        assert mensaje.leido is False
        