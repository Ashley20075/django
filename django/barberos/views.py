from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from citas.models import Cita
from inventario.models import Producto
from .models import Barbero
from django.utils import timezone
from datetime import datetime

@login_required(login_url='login')
def panel_barbero(request):
    """
    Panel del barbero - Muestra solo las citas asignadas a él
    """
    # Obtener el barbero según el email del usuario logueado
    try:
        barbero = Barbero.objects.get(email=request.user.email, activo=True)
    except Barbero.DoesNotExist:
        messages.error(request, 'No tienes un perfil de barbero asignado.')
        return redirect('inicio')
    
    # Obtener todas las citas del barbero
    citas = Cita.objects.filter(barbero=barbero.nombre).order_by('fecha', 'hora')
    
    # ===== FILTROS =====
    estado = request.GET.get('estado')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if estado:
        citas = citas.filter(estado=estado)
    
    if fecha_inicio:
        try:
            fecha_ini = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            citas = citas.filter(fecha__gte=fecha_ini)
        except:
            pass
    
    if fecha_fin:
        try:
            fecha_f = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            citas = citas.filter(fecha__lte=fecha_f)
        except:
            pass
    
    # ===== ESTADÍSTICAS =====
    total_citas = citas.count()
    citas_pendientes = citas.filter(estado='Pendiente').count()
    citas_confirmadas = citas.filter(estado='Confirmada').count()
    citas_canceladas = citas.filter(estado='Cancelada').count()
    
    context = {
        'citas': citas,
        'total_citas': total_citas,
        'citas_pendientes': citas_pendientes,
        'citas_confirmadas': citas_confirmadas,
        'citas_canceladas': citas_canceladas,
        'barbero': barbero,
        'filtro_estado': estado,
        'filtro_fecha_inicio': fecha_inicio,
        'filtro_fecha_fin': fecha_fin,
    }
    return render(request, 'dashboard_barbero.html', context)

@login_required(login_url='login')
def confirmar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    
    # Verificar que la cita pertenece al barbero logueado
    try:
        barbero = Barbero.objects.get(email=request.user.email, activo=True)
        if cita.barbero != barbero.nombre:
            messages.error(request, '❌ No tienes permiso para confirmar esta cita.')
            return redirect('barberos:panel_barbero')
    except Barbero.DoesNotExist:
        messages.error(request, '❌ No tienes un perfil de barbero asignado.')
        return redirect('barberos:panel_barbero')
    
    cita.estado = "Confirmada"
    cita.save()
    messages.success(request, f'✅ Cita de {cita.cliente} confirmada.')
    return redirect('barberos:panel_barbero')

@login_required(login_url='login')
def cancelar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    
    # Verificar que la cita pertenece al barbero logueado
    try:
        barbero = Barbero.objects.get(email=request.user.email, activo=True)
        if cita.barbero != barbero.nombre:
            messages.error(request, '❌ No tienes permiso para cancelar esta cita.')
            return redirect('barberos:panel_barbero')
    except Barbero.DoesNotExist:
        messages.error(request, '❌ No tienes un perfil de barbero asignado.')
        return redirect('barberos:panel_barbero')

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
        messages.success(request, f'✅ Cita de {cita.cliente} cancelada.')

    return redirect('barberos:panel_barbero')

@login_required
def lista_barberos(request):
    barberos = Barbero.objects.filter(activo=True)
    return render(request, 'barberos/lista.html', {'barberos': barberos})

@login_required
def detalle_barbero(request, id):
    barbero = get_object_or_404(Barbero, id=id)
    return render(request, 'barberos/detalle.html', {'barbero': barbero})