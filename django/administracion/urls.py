from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('asignar-barbero/<int:id>/', views.asignar_barbero, name='asignar_barbero'),
    path('quitar-barbero/<int:id>/', views.quitar_barbero, name='quitar_barbero'),
    path('crear-usuario/', views.crear_usuario, name='crear_usuario'),  
    path('editar-cita/<int:id>/', views.editar_cita, name='editar_cita'),
    path('eliminar-cita/<int:id>/', views.eliminar_cita, name='eliminar_cita'),
    path('agregar-barbero/', views.agregar_barbero, name='agregar_barbero'),
    path('editar-barbero/<int:id>/', views.editar_barbero, name='editar_barbero'),
    path('eliminar-barbero/<int:id>/', views.eliminar_barbero, name='eliminar_barbero'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('editar-producto/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar-producto/<int:id>/', views.eliminar_producto_admin, name='eliminar_producto_admin'),
    path('agregar-servicio/', views.agregar_servicio, name='agregar_servicio'),
    path('editar-servicio/<int:id>/', views.editar_servicio, name='editar_servicio'),
    path('eliminar-servicio/<int:id>/', views.eliminar_servicio, name='eliminar_servicio'),
]