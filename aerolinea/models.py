from django import forms
from django.db import models
from django.core.validators import EmailValidator, MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta, date
from decimal import Decimal
import re
import math
import pytz
import random
import string

# Zonas horarias de los destinos internacionales
ZONAS_HORARIAS_DESTINOS = {
    "MADRID": "Europe/Madrid",      # UTC+1 (UTC+2 en verano)
    "LONDRES": "Europe/London",     # UTC+0 (UTC+1 en verano)
    "NUEVA_YORK": "America/New_York",  # UTC-5 (UTC-4 en verano)
    "BUENOS_AIRES": "America/Argentina/Buenos_Aires",  # UTC-3
    "MIAMI": "America/New_York",    # UTC-5 (UTC-4 en verano)
}

# Zona horaria de Colombia (origen)
ZONA_HORARIA_COLOMBIA = "America/Bogota"  # UTC-5


class Pais(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Departamento(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name="departamentos")
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.pais.nombre})"

class Municipio(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name="municipios")
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre} ({self.departamento.nombre})"


# Capitales principales de Colombia
class Capital(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Capital'
        verbose_name_plural = 'Capitales'

    def __str__(self):
        return self.nombre

def calcular_distancia_haversine(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia entre dos puntos usando la fórmula de Haversine
    Retorna la distancia en kilómetros
    """
    # Radio de la Tierra en kilómetros
    R = 6371.0
    
    # Convertir grados a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferencias
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1- a))
    
    # Distancia en kilómetros
    distancia = R * c
    return distancia

# --- Tabla Rol ---
class Rol(models.Model):
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# --- Tabla Usuario ---
class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    email = models.EmailField(unique=True, validators=[EmailValidator(message="Por favor ingresa un correo válido")])
    nombres = models.CharField(max_length=150, null=True, blank=True)
    apellidos = models.CharField(max_length=150, null=True, blank=True)
    direccion_facturacion = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.DateField()
    pais = models.ForeignKey('Pais', on_delete=models.SET_NULL, null=True, blank=True)
    departamento = models.ForeignKey('Departamento', on_delete=models.SET_NULL, null=True, blank=True)
    municipio = models.ForeignKey('Municipio', on_delete=models.SET_NULL, null=True, blank=True)
    dni = models.CharField(max_length=20, unique=True)
    genero = models.CharField(max_length=20, choices=[("M", "Masculino"),("F", "Femenino"), ("O", "Otro"),])
    imagen_usuario = models.ImageField(upload_to="usuarios/", blank=True, null=True)
    es_admin = models.BooleanField(default=False) 
    es_root = models.BooleanField(default=False)
    registro_completo = models.BooleanField(default=False) 
    suscrito_noticias = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

# --- Tabla Vuelo ---
class Vuelo(models.Model):
    TIPO_VUELO = [
        ("NACIONAL", "Nacional"),
        ("INTERNACIONAL", "Internacional"),
    ]

    ORIGEN_INTERNACIONAL = [
        ("PEREIRA", "Pereira"),
        ("BOGOTA", "Bogotá"),
        ("MEDELLIN", "Medellín"),
        ("CALI", "Cali"),
        ("CARTAGENA", "Cartagena"),
        ("MADRID", "Madrid"),
        ("LONDRES", "Londres"),
        ("NUEVA_YORK", "Nueva York"),
        ("BUENOS_AIRES", "Buenos Aires"),
        ("MIAMI", "Miami"),
    ]

    DESTINO_INTERNACIONAL = [
        ("MADRID", "Madrid"),
        ("LONDRES", "Londres"),
        ("NUEVA_YORK", "Nueva York"),
        ("BUENOS_AIRES", "Buenos Aires"),
        ("MIAMI", "Miami"),
        ("PEREIRA", "Pereira"),
        ("BOGOTA", "Bogotá"),
        ("MEDELLIN", "Medellín"),
        ("CALI", "Cali"),
        ("CARTAGENA", "Cartagena"),
    ]
    
    VUELOS_NACIONALES = [
        ("ARAUCA", "Arauca"),
        ("ARMENIA", "Armenia"),
        ("BARRANQUILLA", "Barranquilla"),
        ("BOGOTA", "Bogotá"),
        ("BUCARAMANGA", "Bucaramanga"),
        ("CALI", "Cali"),
        ("CARTAGENA", "Cartagena"),
        ("CUCUTA", "Cucuta"),
        ("FLORENCIA", "Florencia"),
        ("IBAGUE", "Ibagué"),
        ("INIRIDA", "Inirida"),
        ("LETICIA", "Leticia"),
        ("MANIZALES", "Manizales"),
        ("MEDELLIN", "Medellín"),
        ("MITU", "Mitú"),
        ("MOCOA", "Mocoa"),
        ("MONTERIA", "Montería"),
        ("NEIVA", "Neiva"),
        ("PASTO", "Pasto"),
        ("PEREIRA", "Pereira"),
        ("POPAYAN", "Popayán"),
        ("PUERTO_CARREÑO", "Puerto Carreño"),
        ("QUIBDO", "Quibdó"),
        ("RIOHACHA", "Riohacha"),
        ("SAN_ANDRES", "San Andrés"),
        ("SAN_JOSE_DEL_GUAVIARE", "San José del Guaviare"),
        ("SANTA_MARTA", "Santa Marta"),
        ("SINCELEJO", "Sincelejo"),
        ("TUNJA", "Tunja"),
        ("VALLEDUPAR", "Valledupar"),
        ("VILLAVICENCIO", "Villavicencio"),
        ("YOPAL", "Yopal")
    ]

    ESTADOS_VUELO = [
        ('activo', 'Activo'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    ]

    codigo = models.CharField(max_length=20, unique=True, editable=False)
    origen = models.CharField(max_length=50)
    destino = models.CharField(max_length=50)
    estado = models.CharField(max_length=50, choices=ESTADOS_VUELO, default='activo')
    fecha_salida = models.DateField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    fecha_llegada = models.DateField(blank=True, null=True)
    hora_llegada = models.TimeField(blank=True, null=True)
    tiempo_vuelo = models.DurationField(blank=True, null=True, help_text="Tiempo de vuelo calculado automáticamente")
    capacidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0, message="El precio no puede ser negativo")])
    tipo = models.CharField(max_length=20, choices=TIPO_VUELO)
    imagen = models.ImageField(upload_to='vuelos/', blank=True, null=True)
    promocion_activa = models.BooleanField(default=False)
    descuento_porcentaje = models.PositiveIntegerField(
        default=0,
        help_text="Porcentaje de descuento aplicado al vuelo"
    )

    def precio_final(self, usuario=None):
        noticia = Noticia.objects.filter(
            tipo="PROMO",
            vuelo=self,
            activa=True
        ).first()

        if noticia:
            if noticia.solo_suscritos and (not usuario or not usuario.suscrito_noticias):
                return self.precio

            if noticia.descuento_porcentaje:
                return self.precio * (100 - noticia.descuento_porcentaje) / 100

        return self.precio

    def __str__(self):
        return f"{self.codigo} - {self.origen} → {self.destino} ({self.tipo})"

    def establecer_capacidad_automatica(self):
        """
        Establece la capacidad automáticamente según el tipo de vuelo
        Nacional: 150 pasajeros
        Internacional: 250 pasajeros
        """
        if self.tipo == "NACIONAL":
            self.capacidad = 150
        elif self.tipo == "INTERNACIONAL":
            self.capacidad = 250

    def calcular_tiempo_vuelo(self):
        """
        Calcula el tiempo de vuelo basado en la distancia y velocidad del avión
        """
        try:
            # Obtener coordenadas del origen
            origen_capital = Capital.objects.get(nombre__iexact=self.origen)
            
            # Obtener coordenadas del destino
            destino_capital = Capital.objects.get(nombre__iexact=self.destino)
            
            # Calcular distancia usando Haversine
            distancia = calcular_distancia_haversine(
                origen_capital.lat, origen_capital.lon,
                destino_capital.lat, destino_capital.lon
            )
            
            # Velocidad según tipo de vuelo
            if self.tipo == "NACIONAL":
                velocidad = 700  # Airbus A320 km/h
            else:  # INTERNACIONAL
                velocidad = 850  # Airbus A321neo km/h
            
            # Calcular tiempo en horas
            tiempo_horas = (distancia / velocidad) + 0.4
            
            # Convertir a timedelta
            horas = int(tiempo_horas)
            minutos = int((tiempo_horas - horas) * 60)
            
            return timedelta(hours=horas, minutes=minutos)
            
        except Capital.DoesNotExist as e:
            print(f"Error: Capital no encontrada - {e}")
            return None
        except Exception as e:
            print(f"Error calculando tiempo de vuelo: {e}")
            return None

    def calcular_hora_local_destino(self, datetime_utc):
        """
        Convierte un datetime UTC a la hora local del destino
        """
        if self.tipo != "INTERNACIONAL" or self.destino not in ZONAS_HORARIAS_DESTINOS:
            return datetime_utc
        
        try:
            # Obtener la zona horaria del destino
            zona_destino = pytz.timezone(ZONAS_HORARIAS_DESTINOS[self.destino])
            
            # Convertir UTC a hora local del destino
            datetime_local = datetime_utc.astimezone(zona_destino)
            
            return datetime_local
        except Exception as e:
            print(f"Error calculando hora local del destino: {e}")
            return datetime_utc

    def calcular_fecha_llegada(self):
        """
        Calcula la fecha y hora de llegada basada en la salida y tiempo de vuelo
        Considera las zonas horarias para vuelos internacionales
        """
        if not self.fecha_salida or not self.hora_salida:
            return None, None
            
        tiempo_vuelo = self.calcular_tiempo_vuelo()
        if not tiempo_vuelo:
            return None, None
            
        # Crear datetime de salida en zona horaria de Colombia
        zona_colombia = pytz.timezone(ZONA_HORARIA_COLOMBIA)
        datetime_salida_local = datetime.combine(self.fecha_salida, self.hora_salida)
        datetime_salida_local = zona_colombia.localize(datetime_salida_local)
        
        # Convertir a UTC para cálculos
        datetime_salida_utc = datetime_salida_local.astimezone(pytz.UTC)
        
        # Calcular datetime de llegada en UTC
        datetime_llegada_utc = datetime_salida_utc + tiempo_vuelo
        
        # Para vuelos internacionales, convertir a hora local del destino
        if self.tipo == "INTERNACIONAL":
            datetime_llegada_local = self.calcular_hora_local_destino(datetime_llegada_utc)
        else:
            # Para vuelos nacionales, mantener en hora de Colombia
            datetime_llegada_local = datetime_llegada_utc.astimezone(zona_colombia)
        
        return datetime_llegada_local.date(), datetime_llegada_local.time()

    def clean(self):
        """Validaciones personalizadas para vuelos"""
        # Validar salida en el futuro
        if self.fecha_salida and self.hora_salida:
            salida_dt = datetime.combine(self.fecha_salida, self.hora_salida)
            salida_dt = timezone.make_aware(salida_dt, timezone.get_current_timezone())
            if salida_dt < timezone.now():
                raise ValidationError("La fecha de salida no puede estar en el pasado.")

        # Validar llegada después de salida
        if self.fecha_salida and self.hora_salida and self.fecha_llegada and self.hora_llegada:
            salida_dt = datetime.combine(self.fecha_salida, self.hora_salida)
            llegada_dt = datetime.combine(self.fecha_llegada, self.hora_llegada)

            # Asegurar que ambos sean timezone-aware
            salida_dt = timezone.make_aware(salida_dt, timezone.get_current_timezone())
            llegada_dt = timezone.make_aware(llegada_dt, timezone.get_current_timezone())

            if llegada_dt <= salida_dt:
                raise ValidationError("La fecha y hora de llegada deben ser posteriores a la salida.")
        
    def save(self, *args, **kwargs):
        try:
            # Generar código solo si no existe
            if not self.codigo or self.codigo.strip() == "":
                tipo_actual = getattr(self, "tipo", None)
                if not tipo_actual:
                    print("⚠️ Tipo no definido, no se puede generar código aún.")
                else:
                    prefix = "VN" if tipo_actual == "NACIONAL" else "VI"

                    # Buscar el último vuelo de ese tipo
                    last_vuelo = (
                        Vuelo.objects.filter(codigo__startswith=prefix)
                        .order_by('-codigo')
                        .first()
                    )

                    if last_vuelo and last_vuelo.codigo[2:].isdigit():
                        next_num = int(last_vuelo.codigo[2:]) + 1
                    else:
                        next_num = 1

                    self.codigo = f"{prefix}{next_num:04d}"
                    print(f"🟢 Código generado automáticamente: {self.codigo}")

            # Establecer capacidad automáticamente
            self.establecer_capacidad_automatica()

            # Guardar normalmente
            super().save(*args, **kwargs)
            print(f"✅ Vuelo guardado correctamente con código {self.codigo}")

        except Exception as e:
            print("❌ Error en save() de Vuelo:", e)
            raise e

# --- Tabla Reserva ---
class Reserva(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('vencida', 'Vencida'),
        ('confirmada', 'Confirmada'),
        ("pendiente_reubicacion", "Pendiente de Reubicacion"),
    ]

    CLASE_CHOICES = [
        ('economica', 'Económica'),
        ('primera', 'Primera Clase'),
    ]

    TIPO_TRAYECTO = [
        ('ida', 'Solo ida'),
        ('ida_vuelta', 'Ida y Vuelta'),
    ]

    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    vuelo = models.ForeignKey("Vuelo", on_delete=models.CASCADE, related_name="reservas_ida")
    vuelo_regreso = models.ForeignKey("Vuelo", on_delete=models.CASCADE, null=True, blank=True, related_name="reservas_regreso")
    tipo_trayecto = models.CharField(max_length=15, choices=TIPO_TRAYECTO, default="ida")
    clase = models.CharField(max_length=20, choices=CLASE_CHOICES, default='economica')
    num_tiquetes = models.PositiveIntegerField()
    codigo_reserva = models.CharField(max_length=12, unique=True, editable=False)
    asiento_asignado = models.CharField(max_length=5, blank=True, null=True)
    check_in_realizado = models.BooleanField(default=False)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    # hasta cuándo dura la reserva (24h)
    reserved_until = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=50, choices=ESTADOS, default='activa')
    incluye_maleta = models.BooleanField(default=False)

    class Meta:
        # Eliminamos la UniqueConstraint anterior si existe (la revisamos abajo)
        pass

    def save(self, *args, **kwargs):
        if not self.codigo_reserva:
            self.codigo_reserva = self.generar_codigo_reserva()
        # si no hay reserved_until y el estado es activa y no existe compra inmediata,
        # por defecto se reserva 24 horas (puedes ajustar desde vista).
        if not self.reserved_until and self.estado == 'activa':
            self.reserved_until = timezone.now() + timedelta(hours=24)
        # Asignar asiento aleatorio si no existe
        if not self.asiento_asignado:
            self.asiento_asignado = self.generar_asiento()
        super().save(*args, **kwargs)

    def generar_codigo_reserva(self):
        import random, string
        letras = ''.join(random.choices(string.ascii_uppercase, k=2))
        numeros = ''.join(random.choices(string.digits, k=4))
        return f"RES-{letras}{numeros}"

    def generar_asiento(self):
        import random
        fila = random.randint(1, 30)
        columna = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
        return f"{fila}{columna}"

    def esta_vencida(self):
        return self.estado == 'activa' and self.reserved_until and timezone.now() > self.reserved_until

    def __str__(self):
        return f"{self.usuario} - {self.vuelo} {(self.tipo_trayecto)}"

# --- Tabla para cada pasajero incluido en una reserva/compra ---
class ReservaPasajero(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='pasajeros')
    documento = models.CharField(max_length=50)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=20)
    telefono = models.CharField(max_length=30)
    correo = models.EmailField()
    contacto_nombre = models.CharField(max_length=150)
    contacto_telefono = models.CharField(max_length=30)
    asiento = models.CharField(max_length=5, blank=True, null=True)
    check_in_realizado = models.BooleanField(default=False)
    asiento_cambiado = models.BooleanField(default=False)

    class Meta:
        # evitar duplicar mismo pasajero en un mismo vuelo (documento + vuelo)
        constraints = [
            models.UniqueConstraint(
                fields=['documento', 'reserva'],
                name='unique_pasajero_por_reserva'
            )
        ]

    def edad(self):
        hoy = timezone.now().date()
        dob = self.fecha_nacimiento
        return hoy.year - dob.year - ((hoy.month, hoy.day) < (dob.month, dob.day))

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.documento})"


class HistorialVuelo(models.Model):
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE, related_name="historial")
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Historial {self.vuelo.codigo} - {self.estado_anterior} → {self.estado_nuevo}"


class PrecioHistoricoVuelo(models.Model):
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    fecha_registro = models.DateField(auto_now_add=True)
    precio = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.vuelo.codigo_vuelo} - {self.precio} - {self.fecha_registro}"


# --- Tabla Compra ---
class Compra(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    codigo_reserva = models.CharField(max_length=50, unique=True)
    metodo_pago = models.CharField(max_length=50)
    estado = models.CharField(
        max_length=50,
        choices=[
            ('activa', 'Activa'),
            ('cancelada', 'Cancelada'),
            ('reembolsada', 'Reembolsada')
        ],
        default='activa'
    )
    monto_base = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    recargo_clase = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    costo_maleta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reserva = models.ForeignKey(
        'Reserva',            # si Reserva está en la misma app
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compras'
    )
    fecha_compra = models.DateTimeField(auto_now_add=True)
    vuelo_regreso = models.ForeignKey(Vuelo, null=True, blank=True, on_delete=models.SET_NULL, related_name="compras_regreso")
    tipo_trayecto = models.CharField(max_length=20, default="ida")
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Compra {self.codigo_reserva} - {self.usuario.nombre}"

# --- Tabla CheckIn ---
class CheckIn(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    asiento = models.CharField(max_length=5)
    pase_abordar = models.FileField(upload_to='pasabordos/', blank=True, null=True)
    pasajero = models.ForeignKey(ReservaPasajero, on_delete=models.CASCADE, null=True, blank=True)
    fecha_checkin = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CheckIn {self.id} - {self.compra.usuario.nombre}"

# --- Tabla Maleta ---
class Maleta(models.Model):
    checkin = models.ForeignKey(CheckIn, on_delete=models.CASCADE)
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Maleta {self.id} - {self.checkin.compra.usuario.nombre}"

# --- Historial de operaciones ---
class HistorialOperacion(models.Model):
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    tipo = models.CharField(
        max_length=30,
        choices=[
            ("reserva", "Reserva"),
            ("compra", "Compra"),
            ("cancelacion", "Cancelación"),
            ("checkin", "Check-In")
        ]
    )
    descripcion = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.tipo} - {self.usuario.nombre} ({self.fecha.date()})"

# --- Foro: Publicaciones ---
class Publicacion(models.Model):
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.nombre}"

# --- Foro: Comentarios ---
class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Comentario de {self.usuario.nombre}"

# --- Notificaciones ---
class Notificacion(models.Model):
    usuario = models.ForeignKey("Usuario", on_delete=models.CASCADE)
    mensaje = models.TextField()
    enviada = models.BooleanField(default=False)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notificación a {self.usuario.nombre} ({'Enviada' if self.enviada else 'Pendiente'})"
    
# --- Gestión Financiera ---
class Tarjeta(models.Model):
    ESTADOS = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('vencida', 'Vencida'),
        ('confirmada', 'Confirmada'),
    ]

    TIPO_CHOICES = [
        ('CREDITO', 'Crédito'),
        ('DEBITO', 'Débito'),
        ('BLOQUEADA', 'Bloqueada'),
        ('VENCIDA', 'Vencida'),
    ]

    estado = models.CharField(max_length=50, choices=ESTADOS, default='activa')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tarjetas")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    numero = models.CharField(max_length=16, unique=True)
    nombre_titular = models.CharField(max_length=100)
    fecha_vencimiento = models.DateField(default=date(2028,12,31))
    cvv = models.CharField(max_length=4)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.tipo} - **** **** **** {self.numero[-4:]} ({self.usuario.username})"

    def esta_vencida(self):
        """ Retorna True si la tarjeta ya venció """
        return date.today() > self.fecha_vencimiento

    def descontar_saldo(self, monto):
        """ Descuenta saldo si la tarjeta está activa, no vencida y tiene fondos suficientes """
        if self.estado != 'activa':
            return False

        if self.saldo < monto:
            self.estado = 'bloqueada'
            self.save()
            return False
        self.saldo -= monto
        self.save()
        return True

    def __str__(self):
        return f"{self.get_tipo_display()} - **** {self.numero[-4:]} ({'Vencida' if self.esta_vencida() else 'Activa'})"

# --- Carrito ---
class Carrito(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

    def total(self):
        """Suma total del carrito."""
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Carrito de {self.usuario.nombre}"

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, null=True, blank=True)
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carrito', 'vuelo')

    def subtotal(self):
        precio_base = self.vuelo.precio * self.cantidad

        if self.reserva.clase == "primera":
            precio_base += precio_base *Decimal("0.30")

        if self.reserva.incluye_maleta:
            precio_base += Decimal("20000") * self.cantidad

        return precio_base

    def __str__(self):
        return f"{self.vuelo.codigo} x {self.cantidad}"

# --- Opciones cuando se cancela Vuelo ---
class Reubicacion(models.Model):
    ESTADOS_REUBICACION = [
        ("pendiente", "Pendiente"),
        ("completada", "Completada"),
    ]
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    vuelo_cancelado = models.ForeignKey(Vuelo, on_delete=models.CASCADE, related_name="cancelado")
    vuelo_nuevo = models.ForeignKey(Vuelo, on_delete=models.SET_NULL, null=True, blank=True, related_name="reubicado")
    estado = models.CharField(max_length=50, choices=ESTADOS_REUBICACION, default="pendiente")  
    # pendiente, completada, rechazada
    fecha = models.DateTimeField(auto_now_add=True)

class Noticia(models.Model):
    TIPO_CHOICES = [
        ("INFO", "Información"),
        ("PROMO", "Promoción"),
        ("ALERTA", "Alerta"),
    ]

    titulo = models.CharField(max_length=120)
    contenido = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    vuelo = models.ForeignKey(
        Vuelo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    descuento_porcentaje = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    activa = models.BooleanField(default=True)
    creada_por = models.ForeignKey(User, on_delete=models.CASCADE)
    creada_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


