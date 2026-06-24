from django.db import models

class Barbero(models.Model):
    nombre = models.CharField(max_length=200)
    cedula = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = 'Barbero'
        verbose_name_plural = 'Barberos'
        ordering = ['nombre']