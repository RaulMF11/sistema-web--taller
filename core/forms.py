from django import forms
from .models import Diagnosticos

class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = Diagnosticos
        # Aquí definimos SOLO los campos que el mecánico debe llenar.
        # Ocultamos los campos de respuesta de la IA (esos se llenan solos).
        fields = [
            'placa',
            'marca', 
            'modelo', 
            'anio', 
            'kilometraje',
            'ultimo_mantenimiento',
            'descripcion_sintomas',
            'sensor_rpm', 
            'sensor_presion_aceite', 
            'sensor_temperatura_motor', 
            'sensor_voltaje_bateria',
            'sensor_velocidad',
            'sensor_nivel_combustible'
        ]
        
        # Etiquetas amigables para que el mecánico entienda qué poner
        labels = {
            'placa': 'Placa del Vehículo',
            'anio': 'Año de Fabricación',
            'ultimo_mantenimiento': 'Fecha Último Mantenimiento',
            'descripcion_sintomas': 'Descripción de la Falla (Síntomas)',
            'sensor_rpm': 'Sensor RPM',
            'sensor_presion_aceite': 'Presión de Aceite (psi)',
            'sensor_temperatura_motor': 'Temperatura Motor (°C)',
            'sensor_voltaje_bateria': 'Voltaje Batería (V)',
            'sensor_velocidad': 'Velocidad (km/h)',
            'sensor_nivel_combustible': 'Nivel Combustible (%)'
        }

        # Widgets para mejorar la apariencia (Bootstrap ayudará, pero esto ajusta tamaños)
        widgets = {
            'descripcion_sintomas': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Ej: El motor hace un ruido metálico al acelerar...'
            }),
            'placa': forms.TextInput(attrs={'placeholder': 'ABC-123'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date'}),
        }