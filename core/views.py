from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DiagnosticoForm
from .models import Diagnosticos
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
import requests
import json
import os

@login_required
def crear_diagnostico(request):
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            # 1. Obtenemos datos limpios del formulario (SIN GUARDAR EN BD AÚN)
            datos = form.cleaned_data
            
            # 2. Preparar JSON para Azure
            payload = {
                "marca": str(datos['marca']), # Asegurar string si es objeto
                "modelo": str(datos['modelo']),
                "anio": datos['anio'],
                "kilometraje": datos['kilometraje'],
                "ultimo_mantenimiento": str(datos['ultimo_mantenimiento']),
                "descripcion_sintomas": datos['descripcion_sintomas'],
                "sensor_rpm": datos.get('sensor_rpm', 0),
                "sensor_presion_aceite": datos.get('sensor_presion_aceite', 0),
                "sensor_temperatura_motor": datos.get('sensor_temperatura_motor', 0),
                "sensor_voltaje_bateria": datos.get('sensor_voltaje_bateria', 0),
                "sensor_velocidad": datos.get('sensor_velocidad', 0),
                "sensor_nivel_combustible": datos.get('sensor_nivel_combustible', 0)
            }

            # 3. Consultar a Azure
            endpoint_url = os.getenv('AZURE_ML_ENDPOINT')
            api_key = os.getenv('AZURE_ML_KEY')
            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}

            try:
                response = requests.post(endpoint_url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    prediccion = response.json()
                    
                    # 4. PASO CRÍTICO: No guardamos. Renderizamos la plantilla de VALIDACIÓN.
                    # Pasamos los datos originales + la respuesta de la IA
                    contexto = {
                        'datos_originales': payload, # Para re-enviar en el paso 2
                        'prediccion_ia': prediccion,
                        'categorias_fallas': ["Motor", "Sistema Eléctrico", "Transmisión", "Frenos", "Combustible"] # O cargar desde BD
                    }
                    return render(request, 'validar_diagnostico.html', contexto)
                
                else:
                    messages.error(request, f"Error IA: {response.text}")
                    return redirect('crear_diagnostico')

            except Exception as e:
                messages.error(request, f"Error de conexión: {str(e)}")
                return redirect('crear_diagnostico')
    else:
        form = DiagnosticoForm()

    return render(request, 'diagnostico_form.html', {'form': form})
@login_required
def guardar_diagnostico_final(request):
    if request.method == 'POST':
        try:
            # 1. Recuperar datos originales (Inputs ocultos del HTML)
            # Nota: Asumimos que los nombres coinciden con el modelo
            diag = Diagnosticos()
            
            # Asignar usuario logueado (SOLUCIÓN AL ID=1)
            diag.usuario = request.user 
            
            # Asignar datos del vehículo y sensores
            diag.marca = request.POST.get('marca')
            diag.modelo = request.POST.get('modelo')
            diag.anio = request.POST.get('anio')
            diag.kilometraje = request.POST.get('kilometraje')
            diag.ultimo_mantenimiento = request.POST.get('ultimo_mantenimiento')
            diag.descripcion_sintomas = request.POST.get('descripcion_sintomas')
            # ... asignar resto de sensores ...

            # 2. Datos de la IA (Siempre se guardan)
            diag.ia_falla_predicha = request.POST.get('ia_falla')
            diag.ia_subfalla_predicha = request.POST.get('ia_subfalla')
            diag.ia_solucion_predicha = request.POST.get('ia_solucion')
            diag.ia_gravedad_predicha = request.POST.get('ia_gravedad')
            diag.ia_confianza = request.POST.get('ia_confianza')

            # 3. Lógica de Validación (REAL vs PREDICHO)
            validacion = request.POST.get('validacion_mecanico') # 'si' o 'no'
            
            if validacion == 'si':
                diag.es_correcto = True
                # Si es correcto, lo Real es igual a lo Predicho
                diag.falla_real = diag.ia_falla_predicha
                diag.subfalla_real = diag.ia_subfalla_predicha
                diag.solucion_real = diag.ia_solucion_predicha
                diag.gravedad_real = diag.ia_gravedad_predicha
            else:
                diag.es_correcto = False
                # Si es incorrecto, tomamos lo que escribió el mecánico
                diag.falla_real = request.POST.get('correccion_falla')
                diag.subfalla_real = request.POST.get('correccion_subfalla')
                diag.solucion_real = request.POST.get('correccion_solucion')
                diag.gravedad_real = request.POST.get('correccion_gravedad')

            diag.fecha_consulta = timezone.now()
            diag.save()
            
            messages.success(request, "Diagnóstico registrado y validado correctamente.")
            return redirect('historial_diagnosticos')

        except Exception as e:
            messages.error(request, f"Error guardando: {str(e)}")
            return redirect('crear_diagnostico')

@login_required
def historial_diagnosticos(request):
    # 1. Obtener todos los diagnósticos ordenados del más reciente al más antiguo
    lista_diagnosticos = Diagnosticos.objects.all().order_by('-fecha_consulta')
    
    # 2. Renderizar la plantilla enviando la lista
    return render(request, 'historial.html', {
        'diagnosticos': lista_diagnosticos
    })
    
@login_required
def detalle_diagnostico(request, id_diagnostico):
    # Buscamos el diagnóstico por su ID único
    diagnostico = get_object_or_404(Diagnosticos, pk=id_diagnostico)
    
    # LÓGICA DE VALIDACIÓN (FEEDBACK)
    if request.method == 'POST':
        accion = request.POST.get('accion')
        
        if accion == 'validar':
            diagnostico.es_correcto = True
            messages.success(request, '¡Diagnóstico validado como CORRECTO!')
        
        elif accion == 'rechazar':
            diagnostico.es_correcto = False
            # Aquí podríamos guardar cuál fue la falla real, por ahora solo marcamos incorrecto
            messages.info(request, 'Diagnóstico marcado como INCORRECTO. Gracias por el feedback.')
            
        diagnostico.save()
        return redirect('historial')

    return render(request, 'detalle_diagnostico.html', {'diag': diagnostico})

@login_required
def dashboard_admin(request):
    # 1. KPIs Generales
    total_diagnosticos = Diagnosticos.objects.count()
    
    # Cálculo de Precisión de la IA (Solo cuenta los que ya fueron validados por humanos)
    validaciones_totales = Diagnosticos.objects.filter(es_correcto__isnull=False).count()
    aciertos = Diagnosticos.objects.filter(es_correcto=True).count()
    
    precision = 0
    if validaciones_totales > 0:
        precision = round((aciertos / validaciones_totales) * 100, 1)

    # 2. Datos para Gráficos
    # Top 5 Fallas más comunes
    fallas_comunes = Diagnosticos.objects.values('ia_falla_predicha')\
        .annotate(total=Count('ia_falla_predicha'))\
        .order_by('-total')[:5]

    # Distribución por Marcas
    marcas_distribucion = Diagnosticos.objects.values('marca')\
        .annotate(total=Count('marca'))\
        .order_by('-total')

    # Preparamos los datos para enviarlos a Chart.js (Listas de Python)
    labels_fallas = [item['ia_falla_predicha'] if item['ia_falla_predicha'] else "Sin Clasificar" for item in fallas_comunes]
    data_fallas = [item['total'] for item in fallas_comunes]
    
    labels_marcas = [item['marca'] if item['marca'] else "Desconocida" for item in marcas_distribucion]
    data_marcas = [item['total'] for item in marcas_distribucion]

    context = {
        'total_diagnosticos': total_diagnosticos,
        'precision_ia': precision,
        'total_validades': validaciones_totales,
        # Datos Gráficos
        'labels_fallas': labels_fallas,
        'data_fallas': data_fallas,
        'labels_marcas': labels_marcas,
        'data_marcas': data_marcas,
    }

    return render(request, 'dashboard.html', context)