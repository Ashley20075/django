from django.urls import path
from . import views

app_name = 'administracion'

urlpatterns = [
    path('admin-panel/', views.panel_admin, name='panel_admin'),
    path('admin-panel/asignar-barbero/<int:id>/', views.asignar_barbero, name='asignar_barbero'),
    path('admin-panel/quitar-barbero/<int:id>/', views.quitar_barbero, name='quitar_barbero'),
    path('admin-panel/editar-cita/<int:id>/', views.editar_cita, name='editar_cita'),
    path('admin-panel/eliminar-cita/<int:id>/', views.eliminar_cita, name='eliminar_cita'),
    path('admin-panel/agregar-barbero/', views.agregar_barbero, name='agregar_barbero'),
    path('admin-panel/editar-barbero/<int:id>/', views.editar_barbero, name='editar_barbero'),
    path('admin-panel/eliminar-barbero/<int:id>/', views.eliminar_barbero, name='eliminar_barbero'),
    path('admin-panel/agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('admin-panel/editar-producto/<int:id>/', views.editar_producto, name='editar_producto'),
    path('admin-panel/eliminar-producto/<int:id>/', views.eliminar_producto_admin, name='eliminar_producto'),
    path('admin-panel/agregar-servicio/', views.agregar_servicio, name='agregar_servicio'),
    path('admin-panel/editar-servicio/<int:id>/', views.editar_servicio, name='editar_servicio'),
    path('admin-panel/eliminar-servicio/<int:id>/', views.eliminar_servicio, name='eliminar_servicio'),
]