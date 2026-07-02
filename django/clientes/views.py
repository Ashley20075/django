from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError

from clientes.models import Cliente
from citas.models import Cita, Servicio
from barberos.models import Barbero
from inventario.models import Producto

@login_required(login_url='login')
def panel_cliente(request):

    cliente, creado = Cliente.objects.get_or_create(
        user=request.user,
        defaults={
            "nombre": f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            "email": request.user.email,
            "telefono": "",
            "cedula": None,
        }
    )

    proximos = Cita.objects.filter(
        cliente=cliente
    ).exclude(
        estado="Cancelada"
    )

    historial = Cita.objects.filter(
        cliente=cliente,
        estado="Cancelada"
    )

    barberos = Barbero.objects.filter(activo=True)
    servicios = Servicio.objects.all()
    productos = Producto.objects.all()

    return render(
        request,
        "dashboard_cliente.html",
        {
            "nombre": cliente.nombre,
            "proximos": proximos,
            "historial": historial,
            "barberos": barberos,
            "servicios": servicios,
            "productos": productos,
        }
    )


@login_required(login_url='login')
def agendar_cita(request):

    if request.method == "POST":

        adicionales = request.POST.getlist("adicionales")
        productos_seleccionados = request.POST.getlist("productos")

        adicionales_str = ", ".join(adicionales) if adicionales else "Ninguno"
        productos_str = ", ".join(productos_seleccionados) if productos_seleccionados else "Ninguno"

        try:

            cliente = Cliente.objects.get(user=request.user)

            barbero = Barbero.objects.get(
                id=request.POST.get("barbero"),
                activo=True
            )

            servicio = Servicio.objects.get(
                id=request.POST.get("servicio")
            )

            fecha = request.POST.get("fecha")
            hora = request.POST.get("hora")

        except (Cliente.DoesNotExist, Barbero.DoesNotExist, Servicio.DoesNotExist):

            messages.error(request, "❌ Datos inválidos.")
            return redirect("panel_cliente")



        cita_existente = Cita.objects.filter(
            barbero=barbero,
            fecha=fecha,
            hora=hora
        ).exclude(
            estado="Cancelada"
        ).first()

        if cita_existente:

            messages.error(
                request,
                f"❌ {barbero.nombre} ya tiene una cita el {fecha} a las {hora}. Selecciona otro horario."
            )

            return redirect("panel_cliente")

        try:

            Cita.objects.create(
                cliente=cliente,
                servicio=servicio,
                barbero=barbero,
                adicionales=adicionales_str,
                productos=productos_str,
                fecha=fecha,
                hora=hora,
                estado="Pendiente",
            )

        except IntegrityError:

            messages.error(
                request,
                "❌ Ese horario fue reservado por otro cliente mientras realizabas la reserva."
            )

            return redirect("panel_cliente")


        for nombre_producto in productos_seleccionados:

            try:

                producto = Producto.objects.get(
                    nombre=nombre_producto
                )

                if producto.stock_actual > 0:

                    producto.stock_actual -= 1
                    producto.save()

            except Producto.DoesNotExist:
                pass

        messages.success(
            request,
            f"✅ Cita agendada exitosamente con {barbero.nombre}."
        )

        return redirect("panel_cliente")

    return redirect("panel_cliente")

@login_required(login_url='login')
def cancelar_cita_cliente(request, id):
    cita = Cita.objects.get(id=id)

    if cita.estado != "Cancelada":

        if cita.productos and cita.productos != "Ninguno":

            productos = cita.productos.split(",")

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

        messages.success(
            request,
            "✅ Cita cancelada exitosamente"
        )

    return redirect("panel_cliente")


# ============================================
# REGISTRO DE CLIENTES
# ============================================

def registro(request):

    if request.method == "POST":

        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        cedula = request.POST.get("cedula")
        telefono = request.POST.get("telefono")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "registro.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este correo electrónico ya está registrado")
            return render(request, "registro.html")

        try:

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=nombre,
                last_name=apellido,
            )

            Cliente.objects.create(
                user=user,
                nombre=f"{nombre} {apellido}",
                cedula=cedula,
                telefono=telefono,
                email=email,
            )

            messages.success(
                request,
                "¡Cuenta creada exitosamente! Ahora inicia sesión."
            )

            return redirect("login")

        except Exception as e:

            messages.error(
                request,
                f"Error al crear usuario: {e}"
            )

            return render(request, "registro.html")

    return render(request, "registro.html")


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada exitosamente")
    return redirect("login")