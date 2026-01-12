from django.urls import path
from . import views

urlpatterns = [
    # Router Inteligente
    path('', views.home_inteligente, name='home'),
    
    # Dashboard y Perfiles
    path('dashboard/', views.dashboard_admin, name='dashboard'),
    path('mecanico/', views.perfil_mecanico, name='perfil_mecanico'),
    
    # Flujo Diagnóstico
    path('crear/', views.crear_diagnostico, name='crear_diagnostico'),
    path('guardar-final/', views.guardar_diagnostico_final, name='guardar_diagnostico_final'), # <--- OJO CON ESTE NOMBRE
    
    # Historial y Detalles
    path('historial/', views.historial_diagnosticos, name='historial'), # <--- ESTE ES EL NOMBRE ESTÁNDAR
    path('detalle/<int:id_diagnostico>/', views.detalle_diagnostico, name='detalle_diagnostico'),
    
    # AJAX
    path('ajax/modelos/', views.cargar_modelos_ajax, name='ajax_load_modelos'),
    path('ajax/buscar-placa/', views.buscar_placa_ajax, name='ajax_buscar_placa'),
    path('cargar-modelos/', views.cargar_modelos_ajax, name='cargar_modelos_ajax'),
]