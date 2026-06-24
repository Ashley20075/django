from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            username = None
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'✅ Bienvenido {user.username}')
            return redirect('administracion:panel_admin')
        else:
            messages.error(request, '❌ Credenciales incorrectas')
            return render(request, 'login.html')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, '✅ Sesión cerrada correctamente')
    return redirect('login')

def registro_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, '❌ Las contraseñas no coinciden')
            return render(request, 'registro.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ Este email ya está registrado')
            return render(request, 'registro.html')
        
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        messages.success(request, '✅ Usuario registrado correctamente')
        return redirect('login')
    
    return render(request, 'registro.html')