from django import forms
from .models import Diagnosticos, Marcas, Modelos

class DiagnosticoForm(forms.ModelForm):
    # --- 1. CAMPOS DE INTERFAZ (UI) ---
    # Estos NO se guardan en BD, solo sirven para que el usuario elija bonito.
    
    # Campo para ESCRIBIR la placa (Permite autos nuevos)
    placa = forms.CharField(
        label="Placa del Vehículo", 
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ABC-123'})
    )

    marca_select = forms.ModelChoiceField(
        queryset=Marcas.objects.all(),
        label="Seleccionar Marca",
        required=True, # Es opcional porque lo que importa es el hidden 'marca'
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_marca_select'})
    )
    
    modelo_select = forms.ModelChoiceField(
        queryset=Modelos.objects.all(),
        label="Seleccionar Modelo",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_modelo_select'})
    )
    # 3. AÑO (Etiqueta cambiada y Obligatorio)
    anio = forms.IntegerField(
        label="Año de Fabricación", # <--- CAMBIO DE TÍTULO
        required=True,              # <--- AHORA ES OBLIGATORIO
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2015'})
    )
    # --- 4. DATOS TÉCNICOS (AHORA OBLIGATORIOS) ---
    kilometraje = forms.IntegerField(
        label="Kilometraje Actual",
        required=True, # <--- OBLIGATORIO
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    ultimo_mantenimiento = forms.DateField(
        label="Último Mantenimiento",
        required=True, # <--- OBLIGATORIO
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    descripcion_sintomas = forms.CharField(
        label="Descripción del Problema",
        required=True, # <--- OBLIGATORIO
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe el ruido, olor o comportamiento...'})
    )
    
    # NUEVO CAMPO: Propietario
    propietario = forms.CharField(
        label="Nombre del Cliente (Propietario)",
        required=False, # Opcional, si no lo llenan ponemos "Cliente Taller"
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'})
    )
    
    class Meta:
        model = Diagnosticos
        # --- 2. CAMPOS REALES (BD) ---
        fields = [
            # NOTA: Quitamos 'placa_ref' de aquí porque usaremos 'placa' (texto)
            'marca',      # Oculto (se llena con JS)
            'modelo',     # Oculto (se llena con JS)
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
            # CAMPOS OCULTOS (La IA necesita texto, no IDs)
            'marca': forms.HiddenInput(attrs={'id': 'id_marca_texto'}),
            'modelo': forms.HiddenInput(attrs={'id': 'id_modelo_texto'}),
            
            # FORMATO Y ESTILOS
            'descripcion_sintomas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe el ruido, olor o comportamiento...'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # SENSORES
            'sensor_rpm': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_presion_aceite': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_temperatura_motor': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_voltaje_bateria': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_velocidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'sensor_nivel_combustible': forms.NumberInput(attrs={'class': 'form-control'}),
            'anio': forms.NumberInput(attrs={'class': 'form-control'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
        # EXCLUIMOS placa_ref (FK) para manejarlo manualmente en la vista
        exclude = [
            'placa_ref', 'usuario', 
            'ia_falla_predicha', 'ia_subfalla_predicha', 'solucion_predicha', 
            'gravedad_predicha', 'ia_confianza', 'es_correcto', 
            'falla_real', 'subfalla_real', 'gravedad_real', 'solucion_real', 
            'fecha_consulta'
        ]