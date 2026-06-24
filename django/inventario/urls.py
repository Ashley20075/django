from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.dashboard_inventario, name='dashboard'),
    path('agregar/', views.agregar_producto, name='agregar'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar'),
    path('movimiento/<int:producto_id>/', views.movimiento_inventario, name='movimiento'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar'),
]