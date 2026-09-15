import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer de WebSocket para el chat de una consulta.
    URL: ws://localhost:8000/ws/chat/<consulta_id>/?token=<jwt>
    """
    
    async def connect(self):
        self.user = self.scope['user']
        
        print(f"[WS DEBUG] user: {self.user}, autenticado: {self.user.is_authenticated}")
        
        if not self.user.is_authenticated:
            print("[WS DEBUG] RECHAZADO: usuario no autenticado")
            await self.close()
            return
        
        self.consulta_id = self.scope['url_route']['kwargs']['consulta_id']
        self.room_group_name = f'chat_{self.consulta_id}'
        
        print(f"[WS DEBUG] user.rol: {self.user.rol}, user.id: {self.user.id}, consulta_id: {self.consulta_id}")
        
        tiene_acceso = await self._verificar_acceso()
        
        print(f"[WS DEBUG] tiene_acceso: {tiene_acceso}")
        
        if not tiene_acceso:
            print("[WS DEBUG] RECHAZADO: sin acceso a la consulta")
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        
        await self.accept()
        
        print("[WS DEBUG] CONEXION ACEPTADA")
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'usuario': self.user.username,
            }
        )
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name,
            )
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'usuario': self.user.username,
                }
            )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        
        tipo = data.get('tipo')
        
        if tipo == 'mensaje':
            contenido = data.get('contenido', '').strip()
            if not contenido:
                return
            
            mensaje = await self._guardar_mensaje(contenido)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'mensaje': mensaje,
                }
            )
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'mensaje',
            'mensaje': event['mensaje'],
        }))
    
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'user_joined',
            'usuario': event['usuario'],
        }))
    
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'user_left',
            'usuario': event['usuario'],
        }))
    
    @database_sync_to_async
    def _verificar_acceso(self):
        from .models import Consulta
        try:
            consulta = Consulta.objects.get(id=self.consulta_id)
        except Consulta.DoesNotExist:
            print(f"[WS DEBUG] Consulta {self.consulta_id} no existe")
            return False
        
        print(f"[WS DEBUG] Consulta encontrada: paciente_id={consulta.paciente_id}, user.id={self.user.id}, user.rol={self.user.rol}")
        
        user = self.user
        if user.rol in ['recepcionista', 'admin']:
            return True
        if user.rol == 'paciente':
            return consulta.paciente_id == user.id
        if user.rol == 'doctor':
            return consulta.asignada_a_id == user.id
        
        return False
    
    @database_sync_to_async
    def _guardar_mensaje(self, contenido):
        from .models import Consulta, Mensaje
        consulta = Consulta.objects.get(id=self.consulta_id)
        mensaje = Mensaje.objects.create(
            consulta=consulta,
            autor=self.user,
            contenido=contenido,
        )
        consulta.save(update_fields=['actualizada'])
        
        return {
            'id': mensaje.id,
            'autor': self.user.username,
            'autor_rol': self.user.rol,
            'contenido': mensaje.contenido,
            'enviado': mensaje.enviado.isoformat(),
        }


class NotificacionesConsumer(AsyncWebsocketConsumer):
    """
    Consumer global de notificaciones para el personal de la clínica.
    URL: ws://localhost:8000/ws/notificaciones/?token=<jwt>
    """
    
    async def connect(self):
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        if self.user.rol == 'paciente':
            await self.close()
            return
        
        self.groups_to_join = ['notificaciones_staff']
        
        if self.user.rol == 'doctor':
            self.groups_to_join.append(f'notificaciones_doctor_{self.user.id}')
        
        for group in self.groups_to_join:
            await self.channel_layer.group_add(group, self.channel_name)
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'groups_to_join'):
            for group in self.groups_to_join:
                await self.channel_layer.group_discard(group, self.channel_name)
    
    async def receive(self, text_data):
        pass
    
    async def nueva_consulta(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'nueva_consulta',
            'consulta_id': event['consulta_id'],
            'paciente': event['paciente'],
            'motivo': event['motivo'],
            'prioridad': event['prioridad'],
        }))
    
    async def nuevo_mensaje(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'nuevo_mensaje',
            'consulta_id': event['consulta_id'],
            'autor': event['autor'],
            'contenido': event['contenido'][:50],
        }))