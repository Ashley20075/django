from django.db import models
from django.core.exceptions import ValidationError

from barberos.models import Barbero
from clientes.models import Cliente


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.PositiveIntegerField()
    duracion = models.PositiveIntegerField(help_text="Duración en minutos")

    def __str__(self):
        return self.nombre


class Cita(models.Model):

    ESTADOS = [
        ("Pendiente", "Pendiente"),
        ("Confirmada", "Confirmada"),
        ("Cancelada", "Cancelada"),
        ("Finalizada", "Finalizada"),
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

    adicionales = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    productos = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )

    fecha = models.DateField()

    hora = models.CharField(
        max_length=20
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )

    class Meta:
        ordering = ["fecha", "hora"]

        constraints = [
            models.UniqueConstraint(
                fields=["barbero", "fecha", "hora"],
                name="cita_unica_por_barbero"
            )
        ]

    def clean(self):

        if self.barbero:

            existe = Cita.objects.filter(
                barbero=self.barbero,
                fecha=self.fecha,
                hora=self.hora
            ).exclude(pk=self.pk)

            if existe.exists():

                raise ValidationError(
                    "Este barbero ya tiene una cita en ese horario."
                )

    def __str__(self):

        nombre_barbero = (
            self.barbero.nombre
            if self.barbero
            else "Sin asignar"
        )

        return (
            f"{self.cliente.nombre} - "
            f"{self.fecha} "
            f"{self.hora} - "
            f"{nombre_barbero}"
        )