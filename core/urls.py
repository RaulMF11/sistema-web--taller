from django.urls import path
from . import views

urlpatterns = [
    # Cuando entres a la raíz (''), ejecuta la vista crear_diagnostico
    path('', views.crear_diagnostico, name='crear_diagnostico'),
]