from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Sum
from .models import Producto, MovimientoInventario
from .forms import ProductoForm, MovimientoForm

@login_required
def dashboard_inventario(request):
    """Vista principal del inventario con estadísticas"""
    productos = Producto.objects.filter(activo=True).order_by('nombre')
    total_productos = productos.count()
    productos_bajo_stock = productos.filter(stock_actual__lte=models.F('stock_minimo')).count()
    ultimos_movimientos = MovimientoInventario.objects.select_related('producto', 'usuario').order_by('-fecha')[:10]
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
            
            if movimiento.tipo == 'ENTRADA':
                producto.stock_actual += movimiento.cantidad
                messages.success(request, f'✅ Entrada registrada. Nuevo stock: {producto.stock_actual}')
            else:
                if producto.stock_actual >= movimiento.cantidad:
                    producto.stock_actual -= movimiento.cantidad
                    messages.success(request, f'✅ Salida registrada. Nuevo stock: {producto.stock_actual}')
                else:
                    messages.error(request, f'❌ Stock insuficiente. Stock actual: {producto.stock_actual}')
                    return redirect('inventario:dashboard')
            
            producto.save()
            movimiento.save()
            return redirect('inventario:dashboard')
    else:
        form = MovimientoForm()
    
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