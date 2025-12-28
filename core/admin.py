from django.contrib import admin
from .models import Marcas, Modelos, Vehiculos, Diagnosticos

# Configuración bonita para el panel
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'propietario', 'anio', 'fecha_registro')
    search_fields = ('placa', 'propietario')

class DiagnosticoAdmin(admin.ModelAdmin):
    list_display = ('id_diagnostico', 'placa_ref', 'usuario', 'ia_falla_predicha', 'fecha_consulta')
    list_filter = ('ia_falla_predicha', 'usuario')

admin.site.register(Marcas)
admin.site.register(Modelos)
admin.site.register(Vehiculos, VehiculoAdmin)
admin.site.register(Diagnosticos, DiagnosticoAdmin)