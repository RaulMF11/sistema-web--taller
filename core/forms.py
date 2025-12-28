from django import forms
from .models import Diagnosticos, Marcas, Modelos, Vehiculos

class DiagnosticoForm(forms.ModelForm):
    # --- CAMPOS EXTRA (No están en BD, solo para la Interfaz) ---
    # Estos crean los desplegables bonitos para que el mecánico elija
    marca_select = forms.ModelChoiceField(
        queryset=Marcas.objects.all(),
        label="Seleccionar Marca",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_marca_select'})
    )
    
    modelo_select = forms.ModelChoiceField(
        queryset=Modelos.objects.all(), # Idealmente se filtra con JS
        label="Seleccionar Modelo",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_modelo_select'})
    )

    class Meta:
        model = Diagnosticos
        fields = [
            'placa_ref',  # <--- CORREGIDO: Ahora usamos la llave foránea
            'marca',      # Campo de texto (se llenará automático con JS)
            'modelo',     # Campo de texto (se llenará automático con JS)
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
        
        widgets = {
            'descripcion_sintomas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe el ruido, olor o comportamiento...'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # Ocultamos los campos de texto porque el usuario usará los desplegables
            'marca': forms.HiddenInput(),
            'modelo': forms.HiddenInput(),
            'placa_ref': forms.Select(attrs={'class': 'form-select'}), # Desplegable de placas registradas
            # Estilos para sensores
            'sensor_rpm': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_presion_aceite': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_temperatura_motor': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_voltaje_bateria': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_velocidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_nivel_combustible': forms.NumberInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Etiqueta opcional para que se entienda mejor
        self.fields['placa_ref'].label = "Placa del Vehículo (Registrados)"