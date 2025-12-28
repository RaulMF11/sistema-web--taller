from django.db import models
from django.contrib.auth.models import User

# TABLAS MAESTRAS (Ahora gestionadas por Django)
class Marcas(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = True  # <--- CAMBIO: Django creará esta tabla
        db_table = 'Marcas'
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre_marca

class Modelos(models.Model):
    id_modelo = models.AutoField(primary_key=True)
    id_marca = models.ForeignKey(Marcas, on_delete=models.CASCADE, db_column='id_marca')
    nombre_modelo = models.CharField(max_length=50)

    class Meta:
        managed = True  # <--- CAMBIO: Django creará esta tabla
        db_table = 'Modelos'
        verbose_name_plural = "Modelos"

    def __str__(self):
        return f"{self.nombre_modelo} ({self.id_marca.nombre_marca})"

# TABLA VEHICULOS
class Vehiculos(models.Model):
    placa = models.CharField(primary_key=True, max_length=20)
    modelo_ia = models.ForeignKey(Modelos, on_delete=models.PROTECT, db_column='id_modelo')
    propietario = models.CharField(max_length=100, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Vehiculos'
        verbose_name_plural = "Vehiculos"

    def __str__(self):
        return f"{self.placa} - {self.propietario}"

# TABLA DIAGNOSTICOS
class Diagnosticos(models.Model):
    id_diagnostico = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='usuario_id')
    placa_ref = models.ForeignKey(Vehiculos, on_delete=models.SET_NULL, db_column='placa', null=True, blank=True)

    # DATOS FLAT (Texto)
    marca = models.CharField(max_length=50, blank=True, null=True)
    modelo = models.CharField(max_length=50, blank=True, null=True)
    anio = models.IntegerField(blank=True, null=True)
    kilometraje = models.IntegerField(blank=True, null=True)
    ultimo_mantenimiento = models.DateField(blank=True, null=True)
    
    # SÍNTOMAS
    descripcion_sintomas = models.TextField(blank=True, null=True)
    sensor_rpm = models.FloatField(blank=True, null=True)
    sensor_presion_aceite = models.FloatField(blank=True, null=True)
    sensor_temperatura_motor = models.FloatField(blank=True, null=True)
    sensor_voltaje_bateria = models.FloatField(blank=True, null=True)
    sensor_velocidad = models.FloatField(blank=True, null=True)
    sensor_nivel_combustible = models.FloatField(blank=True, null=True)

    # OUTPUTS IA
    ia_falla_predicha = models.CharField(max_length=100, blank=True, null=True)
    ia_subfalla_predicha = models.CharField(max_length=100, blank=True, null=True)
    solucion_predicha = models.TextField(blank=True, null=True)
    gravedad_predicha = models.CharField(max_length=50, blank=True, null=True)
    ia_confianza = models.FloatField(blank=True, null=True)
    es_correcto = models.BooleanField(blank=True, null=True)
    
    # GOLDEN DATA
    falla_real = models.CharField(max_length=100, blank=True, null=True)
    subfalla_real = models.CharField(max_length=100, blank=True, null=True)
    gravedad_real = models.CharField(max_length=50, blank=True, null=True)
    solucion_real = models.TextField(blank=True, null=True)
    
    fecha_consulta = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Diagnosticos'
        verbose_name_plural = "Diagnosticos"

    def __str__(self):
        return f"Diag #{self.id_diagnostico}"