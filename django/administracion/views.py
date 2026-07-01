from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group

from citas.models import Cita, Servicio
from clientes.models import Cliente
from barberos.models import Barbero
from inventario.models import Producto


@login_required
def panel_admin(request):
    usuarios = User.objects.all()
    clientes = Cliente.objects.all()
    citas = Cita.objects.all().order_by('-fecha')

    grupo_barberos, _ = Group.objects.get_or_create(
        name='Barberos'
    )

    cantidad_barberos = User.objects.filter(
        groups=grupo_barberos
    ).count()

    barberos = Barbero.objects.all()
    servicios = Servicio.objects.all()
    productos = Producto.objects.all()

    context = {
        'usuarios': usuarios,
        'clientes': clientes,
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

    if Barbero.objects.filter(email=user.email).exists():
        messages.warning(
            request,
            f'⚠️ El usuario "{user.username}" ya es barbero.'
        )
        return redirect('administracion:panel_admin')

    grupo, _ = Group.objects.get_or_create(
        name='Barberos'
    )

    user.groups.add(grupo)

    cliente = get_object_or_404(
        Cliente,
        user=user
    )

    Barbero.objects.create(
        nombre=cliente.nombre,
        cedula=cliente.cedula,
        telefono=cliente.telefono,
        email=cliente.email,
        especialidad="General",
        activo=True
    )

    messages.success(
        request,
        f'✅ Usuario "{user.username}" ahora es barbero.'
    )

    return redirect('administracion:panel_admin')


@login_required
def quitar_barbero(request, id):
    user = get_object_or_404(User, id=id)

    grupo = Group.objects.get(name='Barberos')
    user.groups.remove(grupo)

    Barbero.objects.filter(
        email=user.email
    ).delete()

    messages.success(
        request,
        f'✅ Usuario "{user.username}" ya no es barbero.'
    )

    return redirect('administracion:panel_admin')


@login_required
def editar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)

    if request.method == 'POST':

        cita.cliente = Cliente.objects.get(
            id=request.POST.get('cliente')
        )

        cita.servicio = Servicio.objects.get(
            id=request.POST.get('servicio')
        )

        cita.barbero = Barbero.objects.get(
            id=request.POST.get('barbero')
        )

        cita.fecha = request.POST.get('fecha')
        cita.hora = request.POST.get('hora')
        cita.estado = request.POST.get('estado')

        cita.save()

        messages.success(
            request,
            '✅ Cita actualizada correctamente.'
        )

        return redirect('administracion:panel_admin')

    return redirect('administracion:panel_admin')


@login_required
def eliminar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    cita.delete()

    messages.success(
        request,
        '✅ Cita eliminada correctamente.'
    )

    return redirect('administracion:panel_admin')

@login_required
def agregar_barbero(request):
    if request.method == 'POST':
        try:
            cedula = request.POST.get('cedula')

            if Barbero.objects.filter(cedula=cedula).exists():
                messages.error(
                    request,
                    f'❌ La cédula "{cedula}" ya está registrada.'
                )
                return redirect('administracion:panel_admin')

            barbero = Barbero.objects.create(
                nombre=request.POST.get('nombre'),
                cedula=cedula,
                especialidad=request.POST.get('especialidad'),
                telefono=request.POST.get('telefono'),
                email=request.POST.get('email'),
                activo=True
            )

            messages.success(
                request,
                f'✅ Barbero "{barbero.nombre}" agregado correctamente.'
            )

        except Exception as e:
            messages.error(request, f'❌ Error: {e}')

        return redirect('administracion:panel_admin')

    return redirect('administracion:panel_admin')


@login_required
def crear_usuario(request):
    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        cedula = request.POST.get('cedula')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, '❌ Las contraseñas no coinciden')
            return redirect('administracion:panel_admin')

        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ Este correo ya está registrado')
            return redirect('administracion:panel_admin')

        if Cliente.objects.filter(cedula=cedula).exists():
            messages.error(request, '❌ La cédula ya está registrada')
            return redirect('administracion:panel_admin')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido
            )

            Cliente.objects.create(
                user=user,
                nombre=f"{nombre} {apellido}",
                cedula=cedula,
                telefono=telefono,
                email=email
            )

            messages.success(
                request,
                f'✅ Usuario "{nombre} {apellido}" creado correctamente.'
            )

        except Exception as e:
            messages.error(request, f'❌ {e}')

        return redirect('administracion:panel_admin')

    return redirect('administracion:panel_admin')


@login_required
def editar_barbero(request, id):
    barbero = get_object_or_404(Barbero, id=id)

    if request.method == 'POST':
        barbero.nombre = request.POST.get('nombre')
        barbero.cedula = request.POST.get('cedula')
        barbero.especialidad = request.POST.get('especialidad')
        barbero.telefono = request.POST.get('telefono')
        barbero.email = request.POST.get('email')

        barbero.save()

        messages.success(
            request,
            '✅ Barbero actualizado correctamente.'
        )

    return redirect('administracion:panel_admin')


@login_required
def eliminar_barbero(request, id):
    barbero = get_object_or_404(Barbero, id=id)

    nombre = barbero.nombre

    barbero.delete()

    messages.success(
        request,
        f'✅ Barbero "{nombre}" eliminado correctamente.'
    )

    return redirect('administracion:panel_admin')

@login_required
def agregar_producto(request):
    if request.method == 'POST':

        Producto.objects.create(
            nombre=request.POST.get('nombre'),
            precio_unitario=request.POST.get('precio'),
            stock_actual=request.POST.get('stock')
        )

        messages.success(
            request,
            f'✅ Producto "{request.POST.get("nombre")}" agregado correctamente.'
        )

    return redirect('administracion:panel_admin')


@login_required
def editar_producto(request, id):
    producto = get_object_or_404(
        Producto,
        id=id
    )

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio_unitario = request.POST.get('precio')
        producto.stock_actual = request.POST.get('stock')

        producto.save()

        messages.success(
            request,
            '✅ Producto actualizado correctamente.'
        )

    return redirect('administracion:panel_admin')


@login_required
def eliminar_producto_admin(request, id):
    producto = get_object_or_404(
        Producto,
        id=id
    )

    nombre = producto.nombre

    producto.delete()

    messages.success(
        request,
        f'✅ Producto "{nombre}" eliminado correctamente.'
    )

    return redirect('administracion:panel_admin')


@login_required
def agregar_servicio(request):
    if request.method == 'POST':

        Servicio.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion'),
            precio=request.POST.get('precio'),
            duracion=request.POST.get('duracion')
        )

        messages.success(
            request,
            f'✅ Servicio "{request.POST.get("nombre")}" agregado correctamente.'
        )

    return redirect('administracion:panel_admin')


@login_required
def editar_servicio(request, id):
    servicio = get_object_or_404(
        Servicio,
        id=id
    )

    if request.method == 'POST':
        servicio.nombre = request.POST.get('nombre')
        servicio.descripcion = request.POST.get('descripcion')
        servicio.precio = request.POST.get('precio')
        servicio.duracion = request.POST.get('duracion')

        servicio.save()

        messages.success(
            request,
            '✅ Servicio actualizado correctamente.'
        )

    return redirect('administracion:panel_admin')


@login_required
def eliminar_servicio(request, id):
    servicio = get_object_or_404(
        Servicio,
        id=id
    )

    nombre = servicio.nombre

    servicio.delete()

    messages.success(
        request,
        f'✅ Servicio "{nombre}" eliminado correctamente.'
    )

    return redirect('administracion:panel_admin')

@login_required
def desactivar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)

    usuario.is_active = False
    usuario.save()

    messages.success(
        request,
        f'✅ El usuario "{usuario.username}" fue desactivado.'
    )

    return redirect('administracion:panel_admin')


@login_required
def activar_usuario(request, id):
    usuario = get_object_or_404(User, id=id)

    usuario.is_active = True
    usuario.save()

    messages.success(
        request,
        f'✅ El usuario "{usuario.username}" fue activado.'
    )

    return redirect('administracion:panel_admin')