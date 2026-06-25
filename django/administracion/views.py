from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from citas.models import Cita, Servicio

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

    # Verificar si el usuario ya es barbero
    if Barbero.objects.filter(email=user.email).exists():
        messages.warning(request, f'⚠️ El usuario "{user.username}" ya es barbero.')
        return redirect('administracion:panel_admin')

    # Agregar al grupo Barberos
    group, created = Group.objects.get_or_create(name='Barberos')
    user.groups.add(group)

    # Crear el barbero con cédula única
    nombre_completo = f"{user.first_name} {user.last_name}".strip()
    nombre_final = nombre_completo if nombre_completo else user.username

    # Generar una cédula única basada en el ID del usuario
    cedula_unica = f"USR{user.id:06d}"  # Ejemplo: USR000006

    Barbero.objects.create(
        nombre=nombre_final,
        cedula=cedula_unica,  # <-- Cédula única generada
        especialidad="General",
        telefono="Sin registrar",
        email=user.email,
        activo=True
    )

    messages.success(
        request,
        f'✅ Usuario "{user.username}" ahora es barbero con cédula {cedula_unica}.'
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
            cedula = request.POST.get('cedula')
            
            # Verificar si la cédula ya existe
            if Barbero.objects.filter(cedula=cedula).exists():
                messages.error(request, f'❌ La cédula "{cedula}" ya está registrada.')
                return redirect('administracion:panel_admin')
            
            barbero = Barbero.objects.create(
                nombre=request.POST.get('nombre'),
                cedula=cedula,
                especialidad=request.POST.get('especialidad'),
                telefono=request.POST.get('telefono'),
                email=request.POST.get('email'),
                activo=True
            )
            messages.success(request, f'✅ Barbero "{barbero.nombre}" agregado correctamente.')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
        return redirect('administracion:panel_admin')
    return redirect('administracion:panel_admin')

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ El nombre de usuario ya existe.')
            return redirect('administracion:panel_admin')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ El email ya está registrado.')
            return redirect('administracion:panel_admin')
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, f'✅ Usuario "{username}" creado exitosamente.')
        return redirect('administracion:panel_admin')
    
    return redirect('administracion:panel_admin')

def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        cedula = request.POST.get('cedula')
        telefono = request.POST.get('telefono')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            messages.error(request, '❌ Las contraseñas no coinciden')
            return redirect('administracion:panel_admin')
        
        # Validar que el email no exista
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ Este correo electrónico ya está registrado')
            return redirect('administracion:panel_admin')
        
        # Validar que el usuario no exista
        if User.objects.filter(username=email).exists():
            messages.error(request, '❌ Este nombre de usuario ya existe')
            return redirect('administracion:panel_admin')
        
        # Validar que la cédula no exista (si se proporcionó)
        if cedula and Barbero.objects.filter(cedula=cedula).exists():
            messages.error(request, '❌ Esta cédula ya está registrada')
            return redirect('administracion:panel_admin')
        
        try:
            # Crear el usuario (usando email como username)
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido
            )
            
            # Crear el cliente asociado (si existe el modelo Cliente)
            try:
                from clientes.models import Cliente
                Cliente.objects.create(
                    user=user,
                    nombre=f"{nombre} {apellido}",
                    cedula=cedula if cedula else "Sin registrar",
                    telefono=telefono if telefono else "Sin registrar",
                    email=email
                )
            except:
                pass
            
            
            messages.success(request, f'✅ Usuario "{nombre} {apellido}" creado exitosamente.')
        except Exception as e:
            messages.error(request, f'❌ Error al crear usuario: {str(e)}')
        
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