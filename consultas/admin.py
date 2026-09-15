from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Consulta, Mensaje


class CustomUserCreationForm(UserCreationForm):
    """Formulario para crear usuarios con campos personalizados."""
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'rol', 'telefono', 'especialidad')


class CustomUserChangeForm(UserChangeForm):
    """Formulario para editar usuarios con campos personalizados."""
    
    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    
    list_display = ('username', 'email', 'rol', 'especialidad', 'is_staff', 'is_active')
    list_filter = ('rol', 'especialidad', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'telefono')
    
    # Campos al CREAR usuario nuevo
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'rol', 'telefono', 'especialidad', 'password1', 'password2'),
        }),
    )
    
    # Campos al EDITAR usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Datos de la clínica', {
            'fields': ('rol', 'telefono', 'especialidad')
        }),
    )


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('id', 'motivo', 'paciente', 'asignada_a', 'estado', 'prioridad', 'creada')
    list_filter = ('estado', 'prioridad', 'creada')
    search_fields = ('motivo', 'descripcion', 'paciente__username')
    readonly_fields = ('creada', 'actualizada')
    date_hierarchy = 'creada'


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'consulta', 'autor', 'contenido_corto', 'leido', 'enviado')
    list_filter = ('leido', 'enviado')
    search_fields = ('contenido', 'autor__username')
    readonly_fields = ('enviado',)
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + ('...' if len(obj.contenido) > 50 else '')
    contenido_corto.short_description = 'Contenido'