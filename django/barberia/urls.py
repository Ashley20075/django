from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('usuarios.urls')),      # Login
    path('', include('clientes.urls')),      # Cliente, Registro, Logout
    path('', include('barberos.urls')),      # Barbero
    path('', include('citas.urls')),
    path('', include('administracion.urls')),
    path('inventario/', include('inventario.urls')),
]