from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from citas.models import Cita
from inventario.models import Producto
from .models import Barbero  # ✅ Importar Barbero

@login_required(login_url='login')
def panel_barbero(request):
    citas = Cita.objects.all()
    return render(request, 'dashboard_barbero.html', {'citas': citas})

@login_required(login_url='login')
def confirmar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    cita.estado = "Confirmada"
    cita.save()
    messages.success(request, f'✅ Cita de {cita.cliente} confirmada.')
    return redirect('panel_barbero')

@login_required(login_url='login')
def cancelar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)

    if cita.estado != "Cancelada":
        if cita.productos and cita.productos != "Ninguno":
            productos = cita.productos.split(',')
            for nombre_producto in productos:
                nombre_producto = nombre_producto.strip()
                try:
                    producto = Producto.objects.get(nombre=nombre_producto)
                    producto.stock_actual += 1
                    producto.save()
                except Producto.DoesNotExist:
                    pass

        cita.estado = "Cancelada"
        cita.save()
        messages.success(request, f'✅ Cita de {cita.cliente} cancelada. Stock restaurado.')

    return redirect('panel_barbero')

# ===== FUNCIONES PARA GESTIONAR BARBEROS (DESDE EL PANEL ADMIN) =====

@login_required
def lista_barberos(request):
    barberos = Barbero.objects.filter(activo=True)
    return render(request, 'barberos/lista.html', {'barberos': barberos})

@login_required
def detalle_barbero(request, id):
    barbero = get_object_or_404(Barbero, id=id)
    return render(request, 'barberos/detalle.html', {'barbero': barbero})