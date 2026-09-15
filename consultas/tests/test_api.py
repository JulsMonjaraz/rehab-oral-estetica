import pytest
from rest_framework.test import APIClient
from rest_framework import status

from consultas.models import Consulta, Mensaje
from .factories import (
    PacienteFactory, DoctorFactory, RecepcionistaFactory, AdminFactory,
    ConsultaFactory,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestAutenticacion:
    def test_sin_token_devuelve_401(self, api_client):
        response = api_client.get('/api/consultas/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_con_token_devuelve_200(self, api_client):
        paciente = PacienteFactory()
        api_client.force_authenticate(user=paciente)
        response = api_client.get('/api/consultas/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUserMe:
    def test_me_devuelve_usuario_actual(self, api_client):
        admin = AdminFactory(username='admin_test')
        api_client.force_authenticate(user=admin)
        response = api_client.get('/api/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'admin_test'
        assert response.data['rol'] == 'admin'


@pytest.mark.django_db
class TestConsultasPermisos:
    def test_paciente_solo_ve_sus_consultas(self, api_client):
        paciente1 = PacienteFactory()
        paciente2 = PacienteFactory()
        ConsultaFactory(paciente=paciente1, motivo='Mía')
        ConsultaFactory(paciente=paciente2, motivo='Ajena')
        
        api_client.force_authenticate(user=paciente1)
        response = api_client.get('/api/consultas/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['motivo'] == 'Mía'

    def test_doctor_solo_ve_consultas_asignadas(self, api_client):
        doctor = DoctorFactory()
        paciente = PacienteFactory()
        ConsultaFactory(paciente=paciente, asignada_a=doctor, motivo='Asignada')
        ConsultaFactory(paciente=paciente, motivo='No asignada')
        
        api_client.force_authenticate(user=doctor)
        response = api_client.get('/api/consultas/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['motivo'] == 'Asignada'

    def test_admin_ve_todas_las_consultas(self, api_client):
        admin = AdminFactory()
        ConsultaFactory()
        ConsultaFactory()
        ConsultaFactory()
        
        api_client.force_authenticate(user=admin)
        response = api_client.get('/api/consultas/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3

    def test_recepcionista_ve_todas_las_consultas(self, api_client):
        recep = RecepcionistaFactory()
        ConsultaFactory()
        ConsultaFactory()
        
        api_client.force_authenticate(user=recep)
        response = api_client.get('/api/consultas/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2


@pytest.mark.django_db
class TestCrearConsulta:
    def test_paciente_puede_crear_consulta(self, api_client):
        paciente = PacienteFactory()
        api_client.force_authenticate(user=paciente)
        
        data = {
            'motivo': 'Dolor de muela',
            'descripcion': 'Me duele mucho',
            'prioridad': 'urgente',
        }
        response = api_client.post('/api/consultas/', data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        consulta = Consulta.objects.get(id=response.data['id'])
        assert consulta.paciente == paciente


@pytest.mark.django_db
class TestAsignarConsulta:
    def test_admin_puede_asignar_doctor(self, api_client):
        admin = AdminFactory()
        doctor = DoctorFactory()
        consulta = ConsultaFactory()
        
        api_client.force_authenticate(user=admin)
        response = api_client.post(
            f'/api/consultas/{consulta.id}/asignar/',
            {'doctor_id': doctor.id},
            format='json',
        )
        
        assert response.status_code == status.HTTP_200_OK
        consulta.refresh_from_db()
        assert consulta.asignada_a == doctor
        assert consulta.estado == 'en_atencion'

    def test_paciente_no_puede_asignar(self, api_client):
        paciente = PacienteFactory()
        doctor = DoctorFactory()
        consulta = ConsultaFactory(paciente=paciente)
        
        api_client.force_authenticate(user=paciente)
        response = api_client.post(
            f'/api/consultas/{consulta.id}/asignar/',
            {'doctor_id': doctor.id},
            format='json',
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_asignar_sin_doctor_id_devuelve_400(self, api_client):
        admin = AdminFactory()
        consulta = ConsultaFactory()
        
        api_client.force_authenticate(user=admin)
        response = api_client.post(
            f'/api/consultas/{consulta.id}/asignar/',
            {},
            format='json',
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCerrarConsulta:
    def test_admin_puede_cerrar_consulta(self, api_client):
        admin = AdminFactory()
        consulta = ConsultaFactory()
        
        api_client.force_authenticate(user=admin)
        response = api_client.post(f'/api/consultas/{consulta.id}/cerrar/')
        
        assert response.status_code == status.HTTP_200_OK
        consulta.refresh_from_db()
        assert consulta.estado == 'cerrada'


@pytest.mark.django_db
class TestMensajesAPI:
    def test_paciente_puede_crear_mensaje_en_su_consulta(self, api_client):
        paciente = PacienteFactory()
        consulta = ConsultaFactory(paciente=paciente)
        
        api_client.force_authenticate(user=paciente)
        response = api_client.post(
            '/api/mensajes/',
            {'consulta': consulta.id, 'contenido': 'Hola doctor'},
            format='json',
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        mensaje = Mensaje.objects.get(id=response.data['id'])
        assert mensaje.autor == paciente
        assert mensaje.contenido == 'Hola doctor'

    def test_paciente_no_puede_escribir_en_consulta_ajena(self, api_client):
        paciente1 = PacienteFactory()
        paciente2 = PacienteFactory()
        consulta_ajena = ConsultaFactory(paciente=paciente2)
        
        api_client.force_authenticate(user=paciente1)
        response = api_client.post(
            '/api/mensajes/',
            {'consulta': consulta_ajena.id, 'contenido': 'Hola'},
            format='json',
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN