from django.db import models
from barberos.models import Barbero
from clientes.models import Cliente


class Servicio(models.Model):
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio      = models.IntegerField()
    duracion    = models.IntegerField()

    def __str__(self):
        return self.nombre

class Cita(models.Model):

    ESTADOS = [
    ('Pendiente', 'Pendiente'),
    ('Confirmada', 'Confirmada'),
    ('Cancelada', 'Cancelada'),
]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="citas"
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE
    )

    barbero = models.ForeignKey(
        Barbero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="citas"
    )

    adicionales = models.CharField(max_length=200, blank=True, default='')
    productos = models.CharField(max_length=200, blank=True, default='')

    fecha = models.DateField()
    hora = models.CharField(max_length=20)

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    ) 
    def __str__(self):
        return f"{self.cliente} - {self.servicio} - {self.fecha} - {self.barbero}"