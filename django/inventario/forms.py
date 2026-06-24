from django import forms
from .models import Producto, MovimientoInventario

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'stock_actual', 'stock_minimo', 'precio_unitario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control bg-dark-input', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control bg-dark-input', 'rows': 3, 'placeholder': 'Descripción opcional'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control bg-dark-input'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control bg-dark-input'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control bg-dark-input', 'step': '0.01'}),
        }

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['tipo', 'cantidad', 'nota']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control bg-dark-input'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control bg-dark-input', 'min': 1}),
            'nota': forms.Textarea(attrs={'class': 'form-control bg-dark-input', 'rows': 2, 'placeholder': 'Observaciones (opcional)'}),
        }