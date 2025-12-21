from django.db import models

# Tabla auxiliar para Marcas (Legado)
class Marcas(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False # Django no modificará la estructura de esta tabla
        db_table = 'Marcas'
    
    def __str__(self):
        return self.nombre_marca

# Tabla auxiliar para Modelos (Legado)
class Modelos(models.Model):
    id_modelo = models.AutoField(primary_key=True)
    id_marca = models.ForeignKey(Marcas, models.DO_NOTHING, db_column='id_marca')
    nombre_modelo = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'Modelos'

    def __str__(self):
        return self.nombre_modelo

# Tabla Principal de Diagnósticos
class Diagnosticos(models.Model):
    id_diagnostico = models.AutoField(primary_key=True)
    # Dejamos id_usuario opcional por ahora hasta integrar el login
    id_usuario = models.IntegerField(blank=True, null=True) 
    
    # Datos del Vehículo
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    kilometraje = models.IntegerField(blank=True, null=True)
    ultimo_mantenimiento = models.DateField(blank=True, null=True)
    placa = models.CharField(max_length=20, blank=True, null=True)
    
    # Síntomas y Sensores (Inputs para la IA)
    descripcion_sintomas = models.TextField(blank=True, null=True)
    sensor_rpm = models.FloatField(blank=True, null=True)
    sensor_presion_aceite = models.FloatField(blank=True, null=True)
    sensor_temperatura_motor = models.FloatField(blank=True, null=True)
    sensor_voltaje_bateria = models.FloatField(blank=True, null=True)
    sensor_velocidad = models.FloatField(blank=True, null=True)
    sensor_nivel_combustible = models.FloatField(blank=True, null=True)

    # Resultados de la IA (Outputs)
    ia_falla_predicha = models.CharField(max_length=100, blank=True, null=True)
    ia_subfalla_predicha = models.CharField(max_length=100, blank=True, null=True)
    ia_confianza = models.FloatField(blank=True, null=True)
    
    # Validación Humana (Feedback)
    es_correcto = models.BooleanField(blank=True, null=True)
    falla_real = models.CharField(max_length=100, blank=True, null=True)
    subfalla_real = models.CharField(max_length=100, blank=True, null=True)
    gravedad_real = models.CharField(max_length=50, blank=True, null=True)
    solucion_real = models.TextField(blank=True, null=True)
    
    # Metadatos
    # IMPORTANTE: Cambiamos esto para que Django ponga la fecha automáticamente al guardar
    fecha_consulta = models.DateTimeField(auto_now_add=True) 

    class Meta:
        managed = False # Indica que la tabla YA existe en Azure
        db_table = 'Diagnosticos'

    def __str__(self):
        return f"Diagnóstico {self.id_diagnostico} - {self.placa}"