from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from citas.models import Cita, Servicio
from usuarios.models import Perfil

try:
    from barberos.models import Barbero
except ImportError:
    from django.db import models
    class Barbero(models.Model):
        nombre = models.CharField(max_length=200)
        cedula = models.CharField(max_length=20)
        especialidad = models.CharField(max_length=100)
        telefono = models.CharField(max_length=20)
        email = models.EmailField()
        fecha_registro = models.DateTimeField(auto_now_add=True)
        activo = models.BooleanField(default=True)
        class Meta:
            managed = False
            db_table = 'barberos_barbero'

from inventario.models import Producto

@login_required
def panel_admin(request):
    usuarios = User.objects.all()
    citas = Cita.objects.all().order_by('-fecha')

    grupo_barberos = Group.objects.get_or_create(
        name='Barberos'
    )[0]

    cantidad_barberos = User.objects.filter(
        groups=grupo_barberos
    ).count()

    barberos = Barbero.objects.all()

    servicios = Servicio.objects.all()
    productos = Producto.objects.all()

    context = {
        'usuarios': usuarios,
        'citas': citas,
        'barberos': barberos,
        'servicios': servicios,
        'productos': productos,
        'cantidad_barberos': cantidad_barberos,
    }

    return render(
        request,
        'administracion/panel_administrador.html',
        context
    )

@login_required
def asignar_barbero(request, id):
    user = get_object_or_404(User, id=id)

    group, created = Group.objects.get_or_create(name='Barberos')
    user.groups.add(group)

    if not Barbero.objects.filter(email=user.email).exists():

        nombre_completo = f"{user.first_name} {user.last_name}".strip()

        try:
            perfil = Perfil.objects.get(usuario=user)

            cedula = perfil.cedula
            telefono = perfil.telefono

        except Perfil.DoesNotExist:

            cedula = "Sin registrar"
            telefono = "Sin registrar"

        Barbero.objects.create(
            nombre=nombre_completo if nombre_completo else user.username,
            cedula=cedula,
            especialidad="General",
            telefono=telefono,
            email=user.email
        )

    messages.success(
        request,
        f'✅ Usuario "{user.username}" ahora es barbero.'
    )

    return redirect('administracion:panel_admin')

@login_required
def quitar_barbero(request, id):
    user = get_object_or_404(User, id=id)

    group = Group.objects.get(name='Barberos')
    user.groups.remove(group)

    Barbero.objects.filter(email=user.email).delete()

    messages.success(
        request,
        f'✅ Usuario "{user.username}" ya no es barbero.'
    )

    return redirect('administracion:panel_admin')

@login_required
def editar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    if request.method == 'POST':
        cita.cliente = request.POST.get('cliente')
        cita.servicio = request.POST.get('servicio')
        cita.fecha = request.POST.get('fecha')
        cita.hora = request.POST.get('hora')
        cita.barbero = request.POST.get('barbero')
        cita.estado = request.POST.get('estado')
        cita.save()
        messages.success(request, '✅ Cita actualizada correctamente.')
        return redirect('administracion:panel_admin')
    return redirect('administracion:panel_admin')

@login_required
def eliminar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    cita.delete()
    messages.success(request, '✅ Cita eliminada correctamente.')
    return redirect('administracion:panel_admin')

@login_required
def agregar_barbero(request):
    if request.method == 'POST':
        try:
            barbero = Barbero.objects.create(
                nombre=request.POST.get('nombre'),
                cedula=request.POST.get('cedula'),
                especialidad=request.POST.get('especialidad'),
                telefono=request.POST.get('telefono'),
                email=request.POST.get('email')
            )
            messages.success(request, f'✅ Barbero "{barbero.nombre}" agregado correctamente.')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
        return redirect('administracion:panel_admin')
    return redirect('administracion:panel_admin')

@login_required
def editar_barbero(request, id):
    try:
        barbero = get_object_or_404(Barbero, id=id)
        if request.method == 'POST':
            barbero.nombre = request.POST.get('nombre')
            barbero.cedula = request.POST.get('cedula')
            barbero.especialidad = request.POST.get('especialidad')
            barbero.telefono = request.POST.get('telefono')
            barbero.email = request.POST.get('email')
            barbero.save()
            messages.success(request, '✅ Barbero actualizado correctamente.')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    return redirect('administracion:panel_admin')

@login_required
def eliminar_barbero(request, id):
    try:
        barbero = get_object_or_404(Barbero, id=id)
        nombre = barbero.nombre
        barbero.delete()
        messages.success(request, f'✅ Barbero "{nombre}" eliminado correctamente.')
    except Exception as e:
        messages.error(request, f'❌ Error: {str(e)}')
    return redirect('administracion:panel_admin')

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        producto = Producto.objects.create(
            nombre=request.POST.get('nombre'),
            precio_unitario=request.POST.get('precio'),
            stock_actual=request.POST.get('stock')
        )
        messages.success(request, f'✅ Producto "{producto.nombre}" agregado correctamente.')
        return redirect('administracion:panel_admin')
    return redirect('administracion:panel_admin')

@login_required
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio_unitario = request.POST.get('precio')
        producto.stock_actual = request.POST.get('stock')
        producto.save()
        messages.success(request, '✅ Producto actualizado correctamente.')
        return redirect('administracion:panel_admin')
    return redirect('administracion:panel_admin')

@login_required
def eliminar_producto_admin(request, id):
    producto = get_object_or_404(Producto, id=id)
    nombre = producto.nombre
    producto.delete()
    messages.success(request, f'✅ Producto "{nombre}" eliminado correctamente.')
    return redirect('administracion:panel_admin')

@login_required
def agregar_servicio(request):
    if request.method == 'POST':
        servicio = Servicio.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion'),
            precio=request.POST.get('precio'),
            duracion=request.POST.get('duracion')
        )
        messages.success(request, f'✅ Servicio "{servicio.nombre}" agregado correctamente.')
        return redirect('administracion:panel_admin')
    return redirect('administracion:panel_admin')

@login_required
def editar_servicio(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    if request.method == 'POST':
        servicio.nombre = request.POST.get('nombre')
        servicio.descripcion = request.POST.get('descripcion')
        servicio.precio = request.POST.get('precio')
        servicio.duracion = request.POST.get('duracion')
        servicio.save()
        messages.success(request, '✅ Servicio actualizado correctamente.')
        return redirect('administracion:panel_admin')
    return redirect('administracion:panel_admin')

@login_required
def eliminar_servicio(request, id):
    servicio = get_object_or_404(Servicio, id=id)
    nombre = servicio.nombre
    servicio.delete()
    messages.success(request, f'✅ Servicio "{nombre}" eliminado correctamente.')
    return redirect('administracion:panel_admin')