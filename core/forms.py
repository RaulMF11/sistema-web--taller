from django import forms
from .models import Diagnosticos, Marcas, Modelos

class DiagnosticoForm(forms.ModelForm):
    # --- 1. CAMPOS DE INTERFAZ (UI) ---
    # Estos se quedan IGUAL porque son útiles para el usuario
    
    placa = forms.CharField(
        label="Placa del Vehículo", 
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ABC-123'})
    )

    marca_select = forms.ModelChoiceField(
        queryset=Marcas.objects.all(),
        label="Seleccionar Marca",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_marca_select'})
    )
    
    modelo_select = forms.ModelChoiceField(
        queryset=Modelos.objects.all(),
        label="Seleccionar Modelo",
        required=True,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_modelo_select'})
    )

    # NUEVO CAMPO: Propietario (UI)
    propietario = forms.CharField(
        label="Nombre del Cliente (Propietario)",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pérez'})
    )
    
    class Meta:
        model = Diagnosticos
        # --- 2. CAMPOS REALES (BD) ---
        # AQUÍ ESTABA EL ERROR: Hemos borrado los sensores de esta lista
        fields = [
            'marca',    # Oculto (se llena con JS)
            'modelo',   # Oculto (se llena con JS)
            'anio', 
            'kilometraje', 
            'ultimo_mantenimiento', 
            'descripcion_sintomas'
        ]
        
        widgets = {
            # CAMPOS OCULTOS (Para que la IA reciba texto)
            'marca': forms.HiddenInput(attrs={'id': 'id_marca_texto'}),
            'modelo': forms.HiddenInput(attrs={'id': 'id_modelo_texto'}),
            
            # FORMATO Y ESTILOS
            'anio': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2015'}),
            'kilometraje': forms.NumberInput(attrs={'class': 'form-control'}),
            'ultimo_mantenimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'descripcion_sintomas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe el ruido, olor o comportamiento...'}),
        }
        
        # EXCLUIMOS lo que no queremos en el form
        exclude = [
            'placa_ref', 'usuario', 
            'ia_falla_predicha', 'ia_subfalla_predicha', 'solucion_predicha', 
            'gravedad_predicha', 'ia_confianza', 'es_correcto', 
            'falla_real', 'subfalla_real', 'gravedad_real', 'solucion_real', 
            'fecha_consulta'
        ]