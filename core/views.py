from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count
import requests
import json
import os

# Importamos Modelos y Formularios
from .models import Diagnosticos, Marcas, Modelos, Vehiculos
from .forms import DiagnosticoForm

# core/views.py

@login_required
def home_inteligente(request):
    if request.user.is_superuser:
        # Si es Admin, va al Dashboard Gerencial
        return redirect('dashboard') 
    else:
        # Si es Mecánico, va a su Perfil Operativo
        return redirect('perfil_mecanico')
    
@login_required
def crear_diagnostico(request):
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        if form.is_valid():
            # 1. Recuperar datos limpios
            placa_txt = form.cleaned_data['placa']
            propietario_txt = form.cleaned_data['propietario']
            
            # --- LÓGICA DE FIDELIZACIÓN ---
            # Buscamos si el vehículo ya existe
            vehiculo, created = Vehiculos.objects.get_or_create(
                placa=placa_txt,
                defaults={
                    # Si es NUEVO, usamos estos datos por defecto
                    'anio': form.cleaned_data['anio'],
                    'propietario': propietario_txt if propietario_txt else "Cliente Taller",
                    'modelo_ia': Modelos.objects.first() # Modelo genérico por ahora
                }
            )
            
            # Si el vehículo YA EXISTÍA y el mecánico escribió un nombre nuevo, actualizamos el dueño
            if not created and propietario_txt:
                vehiculo.propietario = propietario_txt
                vehiculo.save()
            # -------------------------------

            # 2. Guardar Diagnóstico
            diagnostico = form.save(commit=False)
            diagnostico.usuario = request.user # Asignamos al mecánico logueado
            diagnostico.placa_ref = vehiculo   # Enlazamos a la tabla de fidelización
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
                    confianza_raw = prediccion.get('confianza', 0)
                    
                    # Nos aseguramos que sea un número (float)
                    try:
                        confianza_float = float(confianza_raw)
                        # Multiplicamos por 100 y redondeamos a 1 decimal
                        prediccion['confianza'] = round(confianza_float * 100, 1) 
                    except ValueError:
                        prediccion['confianza'] = 0
                    
                    # 4. PASO CRÍTICO: No guardamos. Renderizamos la plantilla de VALIDACIÓN.
                    # Pasamos los datos originales + la respuesta de la IA
                    contexto = {
                        'datos_originales': payload, # Para re-enviar en el paso 2
                        'prediccion_ia': prediccion,
                        'placa_vehiculo': placa_txt,
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
            # Sensores (Usamos '0' si vienen vacíos)
            diag.sensor_rpm = limpiar_numero(request.POST.get('sensor_rpm'))
            diag.sensor_velocidad = limpiar_numero(request.POST.get('sensor_velocidad'))
            diag.sensor_temperatura_motor = limpiar_numero(request.POST.get('sensor_temperatura_motor'))
            diag.sensor_presion_aceite = limpiar_numero(request.POST.get('sensor_presion_aceite'))
            diag.sensor_voltaje_bateria = limpiar_numero(request.POST.get('sensor_voltaje_bateria'))
            diag.sensor_nivel_combustible = limpiar_numero(request.POST.get('sensor_nivel_combustible'))

            # 2. Datos de la IA (Siempre se guardan)
            diag.ia_falla_predicha = request.POST.get('ia_falla')
            diag.ia_subfalla_predicha = request.POST.get('ia_subfalla')
            diag.solucion_predicha = request.POST.get('ia_solucion')
            diag.gravedad_predicha = request.POST.get('ia_gravedad')
            diag.ia_confianza = request.POST.get('ia_confianza')
            
            # --- 3. VINCULACIÓN CON PLACA (CORRECCIÓN) ---
            placa_txt = request.POST.get('placa')
            if placa_txt:
                # Buscamos el objeto Vehiculo para guardarlo en la ForeignKey
                vehiculo = Vehiculos.objects.filter(placa=placa_txt).first()
                if vehiculo:
                    diag.placa_ref = vehiculo # Asignamos la relación

            # 4. Lógica de Validación (REAL vs PREDICHO)
            validacion = request.POST.get('validacion_mecanico') # 'si' o 'no'
            
            if validacion == 'si':
                diag.es_correcto = True
                # Si es correcto, lo Real es igual a lo Predicho
                diag.falla_real = diag.ia_falla_predicha
                diag.subfalla_real = diag.ia_subfalla_predicha
                diag.solucion_real = diag.solucion_predicha
                diag.gravedad_real = diag.gravedad_predicha
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
            return redirect('historial')

        except Exception as e:
            messages.error(request, f"Error guardando: {str(e)}")
            return redirect('crear_diagnostico')

@login_required
def historial_diagnosticos(request):
    # LÓGICA DE FILTRADO
    if request.user.is_superuser:
        # El Admin ve TODO el historial
        lista_diagnosticos = Diagnosticos.objects.all().order_by('-fecha_consulta')
    else:
        # El Mecánico solo ve SUS diagnósticos
        lista_diagnosticos = Diagnosticos.objects.filter(usuario=request.user).order_by('-fecha_consulta')
    
    return render(request, 'historial.html', {
        'diagnosticos': lista_diagnosticos
    })
    
@login_required
def detalle_diagnostico(request, id_diagnostico):
    diagnostico = get_object_or_404(Diagnosticos, pk=id_diagnostico)
    
    # SEGURIDAD: Evitar que un mecánico vea diagnósticos de otro
    if not request.user.is_superuser and diagnostico.usuario != request.user:
        messages.error(request, "No tienes permiso para ver este diagnóstico.")
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

@login_required
def perfil_mecanico(request):
    # 1. KPIs Personales (Solo de ESTE mecánico)
    mis_diagnosticos = Diagnosticos.objects.filter(usuario=request.user)
    total_total = mis_diagnosticos.count()
    
    # 2. Precisión Personal (Feedback)
    # Filtramos los que tienen feedback (True o False)
    validados = mis_diagnosticos.filter(es_correcto__isnull=False).count()
    aciertos = mis_diagnosticos.filter(es_correcto=True).count()
    
    precision = 0
    if validados > 0:
        precision = round((aciertos / validados) * 100, 1)

    # 3. Últimos 5 trabajos realizados
    recientes = mis_diagnosticos.order_by('-fecha_consulta')[:5]

    context = {
        'total': total_total,
        'precision': precision,
        'validados': validados,
        'recientes': recientes
    }
    return render(request, 'perfil_mecanico.html', context)

@login_required
def buscar_placa_ajax(request):
    placa = request.GET.get('placa')
    
    if placa:
        # Buscamos el vehículo por placa
        vehiculo = Vehiculos.objects.filter(placa__iexact=placa).first()
        
        if vehiculo:
            data = {
                'encontrado': True,
                'propietario': vehiculo.propietario,
                'anio': vehiculo.anio,
                # Devolvemos los IDs para seleccionar los dropdowns
                'marca_id': vehiculo.modelo_ia.id_marca.id_marca,
                'modelo_id': vehiculo.modelo_ia.id_modelo,
                # Devolvemos texto también por si acaso
                'marca_nombre': vehiculo.modelo_ia.id_marca.nombre_marca,
                'modelo_nombre': vehiculo.modelo_ia.nombre_modelo
            }
            return JsonResponse(data)
    
    return JsonResponse({'encontrado': False})

@login_required
def cargar_modelos_ajax(request):
    marca_id = request.GET.get('marca_id')
    
    if marca_id:
        # Buscamos modelos que pertenezcan a esa marca
        modelos = Modelos.objects.filter(id_marca_id=marca_id).values('id_modelo', 'nombre_modelo').order_by('nombre_modelo')
        return JsonResponse(list(modelos), safe=False)
    else:
        return JsonResponse([], safe=False)
    
# --- Función Auxiliar para limpiar datos (Pégala antes de la vista) ---
def limpiar_numero(valor):
    """Convierte 'None', '', o None en 0. Si es número, lo devuelve."""
    if valor in [None, 'None', '', 'null']:
        return 0
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0