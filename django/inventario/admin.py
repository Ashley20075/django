from django.contrib import admin
from .models import Producto, MovimientoInventario

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'stock_actual', 'stock_minimo', 'precio_unitario', 'fecha_creacion')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'fecha', 'usuario')
    list_filter = ('tipo', 'fecha')
    search_fields = ('producto__nombre', 'nota')
    readonly_fields = ('fecha',)
    ordering = ('-fecha',)