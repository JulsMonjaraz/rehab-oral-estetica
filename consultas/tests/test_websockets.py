import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import RefreshToken

from config.asgi import application
from consultas.models import Consulta, Mensaje
from .factories import (
    PacienteFactory, DoctorFactory, RecepcionistaFactory, AdminFactory,
    ConsultaFactory,
)


def get_token(user):
    """Genera un JWT para un usuario."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestChatConsumer:
    async def test_conexion_sin_token_rechazada(self):
        """Sin token, la conexión debe rechazarse."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/chat/1/',
        )
        connected, _ = await communicator.connect()
        assert connected is False
        await communicator.disconnect()

    async def test_conexion_con_token_paciente_dueno(self):
        """Un paciente puede conectarse a su propia consulta."""
        paciente = await database_sync_to_async(PacienteFactory)()
        consulta = await database_sync_to_async(ConsultaFactory)(paciente=paciente)
        token = await database_sync_to_async(get_token)(paciente)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/{consulta.id}/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_conexion_paciente_ajeno_rechazada(self):
        """Un paciente NO puede conectarse a la consulta de otro."""
        paciente1 = await database_sync_to_async(PacienteFactory)()
        paciente2 = await database_sync_to_async(PacienteFactory)()
        consulta = await database_sync_to_async(ConsultaFactory)(paciente=paciente2)
        token = await database_sync_to_async(get_token)(paciente1)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/{consulta.id}/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is False
        await communicator.disconnect()

    async def test_admin_puede_conectarse_a_cualquier_consulta(self):
        """El admin puede conectarse a cualquier consulta."""
        admin = await database_sync_to_async(AdminFactory)()
        paciente = await database_sync_to_async(PacienteFactory)()
        consulta = await database_sync_to_async(ConsultaFactory)(paciente=paciente)
        token = await database_sync_to_async(get_token)(admin)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/{consulta.id}/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_enviar_mensaje_guarda_en_bd(self):
        """Enviar un mensaje por WebSocket lo guarda en la BD."""
        paciente = await database_sync_to_async(PacienteFactory)()
        consulta = await database_sync_to_async(ConsultaFactory)(paciente=paciente)
        token = await database_sync_to_async(get_token)(paciente)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/{consulta.id}/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is True
        
        # Ignorar el mensaje de "user_joined"
        await communicator.receive_json_from()
        
        # Enviar un mensaje
        await communicator.send_json_to({
            'tipo': 'mensaje',
            'contenido': 'Hola, me duele la muela',
        })
        
        # Esperar la respuesta
        response = await communicator.receive_json_from()
        assert response['tipo'] == 'mensaje'
        assert response['mensaje']['contenido'] == 'Hola, me duele la muela'
        
        # Verificar que se guardó en la BD
        count = await database_sync_to_async(Mensaje.objects.filter(consulta=consulta).count)()
        assert count == 1
        
        await communicator.disconnect()

    async def test_mensaje_vacio_no_se_guarda(self):
        """Un mensaje vacío no debe guardarse."""
        paciente = await database_sync_to_async(PacienteFactory)()
        consulta = await database_sync_to_async(ConsultaFactory)(paciente=paciente)
        token = await database_sync_to_async(get_token)(paciente)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/chat/{consulta.id}/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is True
        
        await communicator.receive_json_from()  # user_joined
        
        await communicator.send_json_to({
            'tipo': 'mensaje',
            'contenido': '   ',
        })
        
        # No debe recibir respuesta
        assert await communicator.receive_nothing(timeout=0.5)
        
        count = await database_sync_to_async(Mensaje.objects.filter(consulta=consulta).count)()
        assert count == 0
        
        await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestNotificacionesConsumer:
    async def test_paciente_rechazado(self):
        """Un paciente NO puede conectarse al consumer de notificaciones."""
        paciente = await database_sync_to_async(PacienteFactory)()
        token = await database_sync_to_async(get_token)(paciente)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/notificaciones/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is False
        await communicator.disconnect()

    async def test_admin_puede_conectarse(self):
        """El admin SÍ puede conectarse al consumer de notificaciones."""
        admin = await database_sync_to_async(AdminFactory)()
        token = await database_sync_to_async(get_token)(admin)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/notificaciones/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_recepcionista_puede_conectarse(self):
        """La recepcionista SÍ puede conectarse al consumer de notificaciones."""
        recep = await database_sync_to_async(RecepcionistaFactory)()
        token = await database_sync_to_async(get_token)(recep)
        
        communicator = WebsocketCommunicator(
            application,
            f'/ws/notificaciones/?token={token}',
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()