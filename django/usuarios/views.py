from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from barberos.models import Barbero

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            usuario = User.objects.get(email=email)
            username = usuario.username
        except User.DoesNotExist:
            messages.error(request, 'Credenciales inválidas')
            return render(request, 'login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # SUPERUSUARIO → Admin
            if user.is_superuser:
                return redirect('administracion:panel_admin')

            # BARBERO (por email en modelo Barbero)
            try:
                barbero = Barbero.objects.get(email=user.email, activo=True)
                return redirect('barberos:panel_barbero')
            except Barbero.DoesNotExist:
                pass

            # CLIENTE (por defecto)
            return redirect('panel_cliente')

        messages.error(request, 'Credenciales inválidas')
        return render(request, 'login.html')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada exitosamente')
    return redirect('login')

def registro_view(request):
    return redirect('registro')