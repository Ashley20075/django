from django import forms
from .models import Producto, MovimientoInventario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'stock_actual', 'stock_minimo', 'precio_unitario']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control bg-dark-input'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control bg-dark-input'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control bg-dark-input'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control bg-dark-input'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control bg-dark-input', 'step': '0.01'}),
        }

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['tipo', 'cantidad', 'proveedor', 'fecha', 'nota']  # <-- Agregar proveedor y fecha
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select bg-dark-input'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control bg-dark-input', 'min': 1}),
            'proveedor': forms.TextInput(attrs={'class': 'form-control bg-dark-input', 'placeholder': 'Nombre del proveedor'}),
            'fecha': forms.DateTimeInput(attrs={'class': 'form-control bg-dark-input', 'type': 'datetime-local'}),
            'nota': forms.Textarea(attrs={'class': 'form-control bg-dark-input', 'rows': 2, 'placeholder': 'Observaciones del movimiento'}),
        }