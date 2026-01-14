from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

# ----------------------------------------
# PRODUCTOR GANADERO (Modelo principal)
# ----------------------------------------
class Productor(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('REGISTRADO', 'Registrado'),
        ('RENOVACION', 'Renovación'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    dni = models.CharField(max_length=15, unique=True, verbose_name="DNI")
    cuit = models.CharField(max_length=20, blank=True, null=True, verbose_name="CUIT")
    
    # Campos de dirección mejorados
    calle = models.CharField(max_length=300, blank=True, null=True)  # Cambiado de domicilio a calle
    campo = models.CharField(max_length=200, blank=True, null=True)
    localidad = models.CharField(max_length=150, blank=True, null=True)
    municipio = models.CharField(max_length=150, blank=True, null=True)
    departamento = models.CharField(max_length=150, blank=True, null=True)
    provincia = models.CharField(max_length=150, default="Catamarca")
    
    telefono = models.CharField(max_length=80, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Georreferenciación
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    area_hectareas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Productor"
        verbose_name_plural = "Productores"
        ordering = ['apellido', 'nombre']
    
    def __str__(self):
        return f"{self.apellido}, {self.nombre} ({self.dni})"
    
    @property
    def nombre_completo(self):
        return f"{self.apellido}, {self.nombre}"
    
    @property
    def direccion_completa(self):
        parts = []
        if self.calle:
            parts.append(self.calle)
        if self.localidad:
            parts.append(self.localidad)
        if self.municipio:
            parts.append(self.municipio)
        if self.departamento:
            parts.append(self.departamento)
        if self.provincia:
            parts.append(self.provincia)
        return ", ".join(parts)

# ----------------------------------------
# CAMPO
# ----------------------------------------
class Campo(models.Model):
    nombre = models.CharField(max_length=200)
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE, related_name='campos')
    area_hectareas = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    distrito = models.CharField(max_length=150)
    departamento = models.CharField(max_length=150)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    observaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.distrito}"

# ----------------------------------------
# TIPO DE SEÑAL (usando "Senal" sin ñ para evitar problemas)
# ----------------------------------------
class TipoSenal(models.Model):
    UBICACION_OREJA_CHOICES = [
        ('DERECHA', 'Oreja derecha'),
        ('IZQUIERDA', 'Oreja izquierda'),
        ('AMBAS', 'Ambas orejas'),
    ]
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    ubicacion_oreja = models.CharField(max_length=20, choices=UBICACION_OREJA_CHOICES)
    imagen_referencia = models.ImageField(upload_to='referencias/', blank=True, null=True)
    
    def __str__(self):
        return self.nombre

# ----------------------------------------
# MARCA Y SEÑAL (Modelo principal para registros)
# ----------------------------------------


class ImagenMarcaPredefinida(models.Model):
    TIPO_MARCA_CHOICES = [
        ('FLANCO', 'Flanco'),
        ('ANCA', 'Anca'),
        ('COSTILLAR', 'Costillar'),
        ('PALETA', 'Paleta'),
        ('CUELLO', 'Cuello'),
        ('MEJILLA', 'Mejilla'),
        ('OTRO', 'Otro'),
    ]
    
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='marcas/predefinidas/')
    tipo_marca = models.CharField(max_length=20, choices=TIPO_MARCA_CHOICES, default='FLANCO')
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Imagen de Marca Predefinida"
        verbose_name_plural = "Imágenes de Marcas Predefinidas"
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_marca_display()})"



class MarcaSenal(models.Model):  # Sin ñ
    TIPO_TRAMITE_CHOICES = [
        ('NUEVA', 'Marca nueva'),
        ('RENOVACION', 'Renovación'),
        ('TRANSFERENCIA', 'Transferencia'),
    ]
    
    ESTADO_CHOICES = [
        ('VIGENTE', 'Vigente'),
        ('VENCIDA', 'Vencida'),
        ('BAJA', 'Baja'),
        ('EN_TRAMITE', 'En trámite'),
    ]
    
    # Datos básicos
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE, related_name='marcas_senales')
    campo = models.ForeignKey(Campo, on_delete=models.CASCADE, related_name='marcas_senales')
    tipo_tramite = models.CharField(max_length=20, choices=TIPO_TRAMITE_CHOICES, default='NUEVA')
    
    # Información de registro
    numero_orden = models.PositiveIntegerField(unique=True, verbose_name="Número de orden")
    fecha_inscripcion = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    
    # Marcas y señales
    descripcion_marca = models.TextField(verbose_name="Descripción de la marca")
    imagen_marca = models.ImageField(upload_to='marcas/', blank=True, null=True)
    tipo_senal = models.ForeignKey(TipoSenal, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion_senal = models.TextField(blank=True, verbose_name="Descripción de la señal")
    imagen_predefinida = models.ForeignKey(ImagenMarcaPredefinida, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Imagen predefinida")
    
    # Ganado
    vacuno = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    caballar = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    mular = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    asnal = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    ovino = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    cabrio = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Administrativo
    valor_sellado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='EN_TRAMITE')
    observaciones = models.TextField(blank=True)
    
    # Carnet
    imagen_carnet_frente = models.ImageField(upload_to='carnets/', blank=True, null=True)
    imagen_carnet_dorso = models.ImageField(upload_to='carnets/', blank=True, null=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Marca y Señal"
        verbose_name_plural = "Marcas y Señales"
        ordering = ['-fecha_inscripcion']
    
    def __str__(self):
        return f"Marca #{self.numero_orden} - {self.productor}"
    
    @property
    def total_ganado(self):
        return sum([
            self.vacuno, self.caballar, self.mular, 
            self.asnal, self.ovino, self.cabrio
        ])
    


# ----------------------------------------
# SOLICITUD
# ----------------------------------------
class Solicitud(models.Model):
    TIPO_TRAMITE_CHOICES = [
        ('NUEVO', 'Registro nuevo'),
        ('RENOVACION', 'Renovación'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('BAJA', 'Baja'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    
    productor = models.ForeignKey(Productor, on_delete=models.CASCADE, related_name='solicitudes')
    tipo_tramite = models.CharField(max_length=20, choices=TIPO_TRAMITE_CHOICES)
    fecha_solicitud = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    documento_adjunto = models.FileField(upload_to='solicitudes/', blank=True, null=True)
    observaciones = models.TextField(blank=True)
    
    # Relación con marca/señal si aplica
    marca_senal = models.ForeignKey(MarcaSenal, on_delete=models.CASCADE, blank=True, null=True, related_name='solicitudes')
    
    def __str__(self):
        return f"{self.get_tipo_tramite_display()} - {self.productor}"

# ----------------------------------------
# PERFIL DE USUARIO
# ----------------------------------------
class UserProfile(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('inspector', 'Inspector'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='empleado')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"
    
    @property
    def es_administrador(self):
        return self.rol == 'admin'

# ----------------------------------------
# LOG DE CAMBIOS
# ----------------------------------------
class ChangeLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    modelo = models.CharField(max_length=120)
    objeto_id = models.CharField(max_length=120)
    accion = models.CharField(max_length=40)
    timestamp = models.DateTimeField(auto_now_add=True)
    snapshot = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.modelo}:{self.objeto_id} {self.accion} @ {self.timestamp}"