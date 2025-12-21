from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import DiagnosticoForm
import requests
import json
import os

def crear_diagnostico(request):
    # Si el mecánico envió el formulario (Método POST)
    if request.method == 'POST':
        form = DiagnosticoForm(request.POST)
        
        if form.is_valid():
            diagnostico = form.save(commit=False)
            
            # --- 1. Preparar Datos para Azure (Estructura Plana) ---
            datos_para_ia = {
                "marca": diagnostico.marca,
                "modelo": diagnostico.modelo,
                "anio": diagnostico.anio,
                "kilometraje": diagnostico.kilometraje,
                "ultimo_mantenimiento": str(diagnostico.ultimo_mantenimiento),
                "descripcion_sintomas": diagnostico.descripcion_sintomas,
                "sensor_rpm": diagnostico.sensor_rpm or 0,
                "sensor_presion_aceite": diagnostico.sensor_presion_aceite or 0,
                "sensor_temperatura_motor": diagnostico.sensor_temperatura_motor or 0,
                "sensor_voltaje_bateria": diagnostico.sensor_voltaje_bateria or 0,
                "sensor_velocidad": diagnostico.sensor_velocidad or 0,
                "sensor_nivel_combustible": diagnostico.sensor_nivel_combustible or 0
            }

            # --- 2. Configurar Conexión ---
            endpoint_url = os.getenv('AZURE_ML_ENDPOINT')
            api_key = os.getenv('AZURE_ML_KEY')
            headers = {'Content-Type': 'application/json'}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            # --- 3. Enviar y Procesar ---
            try:
                print(f"🚀 Enviando a Azure: {json.dumps(datos_para_ia)}") # Log simple
                
                response = requests.post(endpoint_url, json=datos_para_ia, headers=headers)
                
                print("ESTADO HTTP:", response.status_code)
                print("RESPUESTA CRUDA:", response.text)

                if response.status_code == 200:
                    # AQUI ESTABA EL ERROR: Usamos 'data' que es lo que llega de Azure
                    data = response.json() 
                    
                    # 1. Guardamos en el Modelo (BD) usando 'data'
                    diagnostico.ia_falla_predicha = data.get('falla_predicha', 'Desconocido')
                    diagnostico.ia_subfalla_predicha = data.get('subfalla_predicha', 'N/A')
                    diagnostico.ia_confianza = data.get('confianza', 0.0)
                    
                    # Guardamos en SQL Server
                    diagnostico.save() 

                    # 2. Preparamos el Contexto para el HTML (Esto es lo que verá el usuario)
                    contexto_resultado = {
                        'falla': diagnostico.ia_falla_predicha,
                        'subfalla': diagnostico.ia_subfalla_predicha,
                        'solucion': data.get('solucion_predicha', 'Revisar manual de servicio'),
                        'gravedad': data.get('gravedad_predicha', 'Media'),
                        'confianza': round(diagnostico.ia_confianza * 100, 1),
                        'confianza_decimal': diagnostico.ia_confianza
                    }

                    # ¡IMPORTANTE! Usamos 'render' para quedarnos en la página y mostrar la tarjeta
                    return render(request, 'diagnostico_form.html', {
                        'form': DiagnosticoForm(), # Formulario limpio
                        'resultado': contexto_resultado # Enviamos el resultado
                    })

                else:
                    # Si Azure da error (400, 500)
                    messages.warning(request, f'Error en la IA: {response.text}')

            except Exception as e:
                # Si falla la conexión (Internet, timeout)
                messages.error(request, f'Error crítico de conexión: {str(e)}')

            # Si algo falló (entró al else o al except), guardamos sin IA y recargamos
            diagnostico.save()
            return redirect('crear_diagnostico')

    # Método GET (Carga inicial)
    else:
        form = DiagnosticoForm()

    return render(request, 'diagnostico_form.html', {'form': form})