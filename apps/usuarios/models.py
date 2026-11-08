from django.db import models

class Usuario(models.Model):
    # usuario propio del sitio (clientes y administradores de la agencia).
    ROLES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
    ]

    rut = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.IntegerField()
    correo_electronico = models.EmailField(unique=True)   # se usa como "usuario" para iniciar sesión
    # se guarda tal como se escribe (texto plano).
    contrasena = models.CharField(max_length=128)
    # con este rol las vistas deciden si se permite el acceso a la gestión (ver es_administrador en catalogo).
    rol = models.CharField(max_length=50, choices=ROLES, default='cliente')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"