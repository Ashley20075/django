from django.urls import path
from . import views

app_name = 'barberos'

urlpatterns = [
    path('barbero/', views.panel_barbero, name='panel_barbero'),
    path('confirmar/<int:id>/', views.confirmar_cita, name='confirmar_cita'),
    path('cancelar/<int:id>/', views.cancelar_cita, name='cancelar_cita'),
    path('barberos/', views.lista_barberos, name='lista'),
    path('barberos/<int:id>/', views.detalle_barbero, name='detalle'),
]