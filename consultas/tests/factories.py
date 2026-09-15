import factory
from django.contrib.auth import get_user_model
from consultas.models import Consulta, Mensaje

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    rol = 'paciente'


class PacienteFactory(UserFactory):
    rol = 'paciente'


class DoctorFactory(UserFactory):
    rol = 'doctor'
    especialidad = 'general'


class RecepcionistaFactory(UserFactory):
    rol = 'recepcionista'


class AdminFactory(UserFactory):
    rol = 'admin'


class ConsultaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Consulta
    
    paciente = factory.SubFactory(PacienteFactory)
    motivo = factory.Sequence(lambda n: f'Consulta {n}')
    descripcion = 'Descripción de prueba'
    estado = 'pendiente'
    prioridad = 'normal'


class MensajeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mensaje
    
    consulta = factory.SubFactory(ConsultaFactory)
    autor = factory.SubFactory(PacienteFactory)
    contenido = 'Mensaje de prueba'