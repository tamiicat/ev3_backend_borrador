from django.contrib import admin
from .models import Usuario

# registro de Usuario en /admin/ (no hace falta más comentario: son opciones estándar).
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('rut', 'nombre', 'apellido', 'correo_electronico', 'telefono', 'rol')
    list_filter = ('rol',)
    search_fields = ('rut', 'nombre', 'apellido', 'correo_electronico')
    list_editable = ('rol',)   # el rol se puede cambiar directamente desde el listado
    list_per_page = 20