from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from citas.models import Cita
from inventario.models import Producto
from .models import Barbero
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.conf import settings
import os

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
    citas = Cita.objects.filter(
    barbero=barbero
).order_by('fecha', 'hora')
    
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
        if cita.barbero != barbero:
            messages.error(request, '❌ No tienes permiso para confirmar esta cita.')
            return redirect('barberos:panel_barbero')
    except Barbero.DoesNotExist:
        messages.error(request, '❌ No tienes un perfil de barbero asignado.')
        return redirect('barberos:panel_barbero')
    
    cita.estado = "Confirmada"
    cita.save()
    messages.success(request, f'✅ Cita de {cita.cliente.nombre} confirmada.')
    return redirect('barberos:panel_barbero')

@login_required(login_url='login')
def cancelar_cita(request, id):
    cita = get_object_or_404(Cita, id=id)
    
    # Verificar que la cita pertenece al barbero logueado
    try:
        barbero = Barbero.objects.get(email=request.user.email, activo=True)
        if cita.barbero != barbero:
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
        messages.success(
    request,
    f'✅ Cita de {cita.cliente.nombre} cancelada.'
)

    return redirect('barberos:panel_barbero')

@login_required
def lista_barberos(request):
    barberos = Barbero.objects.filter(activo=True)
    return render(request, 'barberos/lista.html', {'barberos': barberos})

@login_required
def detalle_barbero(request, id):
    barbero = get_object_or_404(Barbero, id=id)
    return render(request, 'barberos/detalle.html', {'barbero': barbero})

@login_required
def certificado_laboral(request):

    try:
        barbero = Barbero.objects.get(
            email=request.user.email,
            activo=True
        )
    except Barbero.DoesNotExist:
        messages.error(request, "No tienes un perfil de barbero.")
        return redirect("barberos:panel_barbero")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificado_laboral.pdf"'

    doc = SimpleDocTemplate(response)

    estilos = getSampleStyleSheet()

    elementos = []

    # Logo

    ruta_logo = os.path.join(
        settings.BASE_DIR,
        "inventario",
        "static",
        "img",
        "logo.jpeg"
    )

    if os.path.exists(ruta_logo):
        logo = Image(ruta_logo)
        logo.drawWidth = 80
        logo.drawHeight = 80
        elementos.append(logo)

    elementos.append(
        Paragraph(
            "<b>CERTIFICADO LABORAL</b>",
            estilos["Title"]
        )
    )

    elementos.append(
        Paragraph(
            "BarberSpringfield",
            estilos["Heading2"]
        )
    )

    elementos.append(
        Paragraph(
            "<br/><br/>Se certifica que:",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"<b>{barbero.nombre}</b>",
            estilos["Heading1"]
        )
    )

    elementos.append(
        Paragraph(
            f"Cédula: {barbero.cedula}",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Especialidad: {barbero.especialidad}",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"Correo: {barbero.email}",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            "<br/>Actualmente se encuentra vinculado laboralmente "
            "como BARBERO en nuestra empresa, desempeñando sus "
            "funciones con responsabilidad y profesionalismo.",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            f"<br/>Fecha de expedición: {datetime.now().strftime('%d/%m/%Y')}",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            "<br/><br/><br/>____________________________",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            "Administrador",
            estilos["Normal"]
        )
    )

    elementos.append(
        Paragraph(
            "Barbería Elegance",
            estilos["Normal"]
        )
    )

    doc.build(elementos)

    return response