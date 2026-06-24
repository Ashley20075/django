from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from citas.models import Cita, Barbero, Servicio
from inventario.models import Producto

# ============================================
# VISTAS DEL PANEL DEL CLIENTE
# ============================================

@login_required(login_url='login')
def panel_cliente(request):
    nombre_cliente = request.user.first_name
    proximos = Cita.objects.filter(cliente=nombre_cliente).exclude(estado="Cancelada")
    historial = Cita.objects.filter(cliente=nombre_cliente, estado="Cancelada")
    barberos = Barbero.objects.all()
    servicios = Servicio.objects.all()
    productos = Producto.objects.all()
    
    return render(request, 'dashboard_cliente.html', {
        'nombre': nombre_cliente,
        'proximos': proximos,
        'historial': historial,
        'barberos': barberos,
        'servicios': servicios,
        'productos': productos,
    })

@login_required(login_url='login')
def agendar_cita(request):
    if request.method == "POST":
        adicionales = request.POST.getlist('adicionales')
        prods_seleccionados = request.POST.getlist('productos')

        adicionales_str = ', '.join(adicionales) if adicionales else 'Ninguno'
        productos_str = ', '.join(prods_seleccionados) if prods_seleccionados else 'Ninguno'

        Cita.objects.create(
            cliente=request.user.first_name,
            servicio=request.POST.get('servicio'),
            adicionales=adicionales_str,
            productos=productos_str,
            fecha=request.POST.get('fecha'),
            hora=request.POST.get('hora'),
            barbero=request.POST.get('barbero'),
            estado="Pendiente",
        )

        # DESCONTAR INVENTARIO
        for nombre_producto in prods_seleccionados:
            try:
                producto = Producto.objects.get(nombre=nombre_producto)
                if producto.stock > 0:
                    producto.stock -= 1
                    producto.save()
            except Producto.DoesNotExist:
                pass

        return redirect('panel_cliente')

    return redirect('panel_cliente')

@login_required(login_url='login')
def cancelar_cita_cliente(request, id):
    cita = Cita.objects.get(id=id)

    # Evitar devolver inventario dos veces
    if cita.estado != "Cancelada":
        if cita.productos and cita.productos != "Ninguno":
            productos = cita.productos.split(',')
            for nombre_producto in productos:
                nombre_producto = nombre_producto.strip()
                try:
                    producto = Producto.objects.get(nombre=nombre_producto)
                    producto.stock += 1
                    producto.save()
                except Producto.DoesNotExist:
                    pass

        cita.estado = "Cancelada"
        cita.save()

    return redirect('panel_cliente')

# ============================================
# VISTAS DE AUTENTICACIÓN (REGISTRO Y LOGIN)
# ============================================

def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'registro.html')
        
        # Validar que el email no exista
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Este correo electrónico ya está registrado')
            return render(request, 'registro.html')
        
        try:
            # Crear el usuario
            user = User.objects.create_user(
                username=email,  # Usamos email como username
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido
            )
            
            messages.success(request, '¡Cuenta creada exitosamente! Ahora inicia sesión.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
            return render(request, 'registro.html')
    
    return render(request, 'registro.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('panel_cliente')
        else:
            messages.error(request, 'Credenciales inválidas')
            return render(request, 'login.html')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('inicio')