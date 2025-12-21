from django.urls import path
from . import views

urlpatterns = [
    # Cuando entres a la raíz (''), ejecuta la vista crear_diagnostico
    path('', views.crear_diagnostico, name='crear_diagnostico'),
    path('historial/', views.historial_diagnosticos, name='historial'),
    path('detalle/<int:id_diagnostico>/', views.detalle_diagnostico, name='detalle_diagnostico'),
]