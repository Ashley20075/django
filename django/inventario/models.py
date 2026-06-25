from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # <-- Agrega esta importación

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    def necesita_reposicion(self):
        return self.stock_actual <= self.stock_minimo
    
    def estado_stock(self):
        if self.stock_actual <= 0:
            return 'agotado'
        elif self.stock_actual <= self.stock_minimo:
            return 'bajo'
        elif self.stock_actual <= self.stock_minimo * 2:
            return 'medio'
        else:
            return 'suficiente'

class MovimientoInventario(models.Model):
    TIPO_MOVIMIENTO = [
        ('ENTRADA', 'Entrada de Stock'),
        ('SALIDA', 'Salida de Stock'),
        ('AJUSTE', 'Ajuste de Stock'),  # <-- NUEVO TIPO
    ]
    
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO)
    cantidad = models.PositiveIntegerField()
    
    # NUEVOS CAMPOS
    stock_anterior = models.PositiveIntegerField(default=0)  # <-- Stock antes del movimiento
    stock_nuevo = models.PositiveIntegerField(default=0)     # <-- Stock después del movimiento
    
    # CAMPOS QUE SOLICITASTE
    proveedor = models.CharField(max_length=200, blank=True, null=True)  # <-- Proveedor
    fecha = models.DateTimeField(default=timezone.now)  # <-- Fecha personalizable (ahora no es auto_now_add)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nota = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})"
    
    def save(self, *args, **kwargs):
        # Guardar stock anterior y calcular nuevo stock
        if not self.pk:  # Si es nuevo movimiento
            self.stock_anterior = self.producto.stock_actual
            
            if self.tipo == 'ENTRADA':
                self.stock_nuevo = self.stock_anterior + self.cantidad
            elif self.tipo == 'SALIDA':
                self.stock_nuevo = self.stock_anterior - self.cantidad
            elif self.tipo == 'AJUSTE':
                self.stock_nuevo = self.cantidad  # El ajuste establece el stock exacto
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-fecha']  # <-- Ordenar por fecha descendente