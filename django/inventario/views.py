from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from .models import Producto, MovimientoInventario
from .forms import ProductoForm, MovimientoForm

@login_required
def dashboard_inventario(request):
    """Vista principal del inventario con estadísticas"""
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    total_productos = productos.count()
    productos_bajo_stock = productos.filter(stock_actual__lte=models.F('stock_minimo')).count()
    ultimos_movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha')[:20]  # <-- Más movimientos
    stock_total = productos.aggregate(total=Sum('stock_actual'))['total'] or 0
    
    context = {
        'productos': productos,
        'total_productos': total_productos,
        'productos_bajo_stock': productos_bajo_stock,
        'stock_total': stock_total,
        'ultimos_movimientos': ultimos_movimientos,
    }
    return render(request, 'inventario/dashboard.html', context)

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f'✅ Producto "{producto.nombre}" agregado exitosamente.')
            return redirect('inventario:dashboard')
    else:
        form = ProductoForm()
    return render(request, 'inventario/producto_form.html', {'form': form, 'titulo': 'Agregar Producto'})

@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Producto "{producto.nombre}" actualizado correctamente.')
            return redirect('inventario:dashboard')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/producto_form.html', {'form': form, 'titulo': 'Editar Producto'})

@login_required
def movimiento_inventario(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.usuario = request.user
            
            # Si no se proporcionó fecha, usar la actual
            if not movimiento.fecha:
                movimiento.fecha = timezone.now()
            
            # Guardar stock anterior
            movimiento.stock_anterior = producto.stock_actual
            
            # Procesar según tipo
            if movimiento.tipo == 'ENTRADA':
                producto.stock_actual += movimiento.cantidad
                movimiento.stock_nuevo = producto.stock_actual
                messages.success(request, f'✅ Entrada registrada. Nuevo stock: {producto.stock_actual}')
                
            elif movimiento.tipo == 'SALIDA':
                if producto.stock_actual >= movimiento.cantidad:
                    producto.stock_actual -= movimiento.cantidad
                    movimiento.stock_nuevo = producto.stock_actual
                    messages.success(request, f'✅ Salida registrada. Nuevo stock: {producto.stock_actual}')
                else:
                    messages.error(request, f'❌ Stock insuficiente. Stock actual: {producto.stock_actual}')
                    return redirect('inventario:dashboard')
                    
            elif movimiento.tipo == 'AJUSTE':  # <-- NUEVO TIPO
                movimiento.stock_nuevo = movimiento.cantidad
                producto.stock_actual = movimiento.cantidad
                messages.success(request, f'✅ Ajuste realizado. Nuevo stock: {producto.stock_actual}')
            
            producto.save()
            movimiento.save()
            return redirect('inventario:dashboard')
    else:
        form = MovimientoForm(initial={'fecha': timezone.now()})  # <-- Fecha por defecto
    
    return render(request, 'inventario/movimiento_form.html', {
        'form': form,
        'producto': producto
    })

@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'✅ Producto "{nombre}" eliminado correctamente.')
        return redirect('inventario:dashboard')
    return render(request, 'inventario/eliminar_confirm.html', {'producto': producto})

# ========== NUEVA VISTA: HISTORIAL COMPLETO ==========
@login_required
def historial_movimientos(request):
    movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha')
    
    # Filtros
    tipo = request.GET.get('tipo')
    producto_id = request.GET.get('producto')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if tipo:
        movimientos = movimientos.filter(tipo=tipo)
    if producto_id:
        movimientos = movimientos.filter(producto_id=producto_id)
    if fecha_inicio:
        movimientos = movimientos.filter(fecha__date__gte=fecha_inicio)
    if fecha_fin:
        movimientos = movimientos.filter(fecha__date__lte=fecha_fin)
    
    productos = Producto.objects.filter(activo=True)
    
    context = {
        'movimientos': movimientos,
        'productos': productos,
        'tipos': MovimientoInventario.TIPO_MOVIMIENTO,
    }
    return render(request, 'inventario/historial_movimientos.html', context)