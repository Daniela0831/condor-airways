from django.contrib import admin
from .models import Rol, Usuario, Vuelo, Reserva, Compra, CheckIn, Maleta, Capital
from .forms import VueloAdminForm, ReservaForm
from django.urls import path
from django.http import JsonResponse
from django.utils.html import format_html

# Mostrar columnas clave en el admin
@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    form = VueloAdminForm
    list_display = (
        "id",
        "codigo",
        "origen",
        "destino",
        "fecha_salida",
        "hora_salida",
        "fecha_llegada",
        "hora_llegada",
        "tiempo_vuelo",
        "precio",
    )
    list_filter = ("origen", "destino")
    search_fields = ("codigo", "origen", "destino")

    readonly_fields = ("codigo_preview", "codigo")
    fieldsets = (
        (
            "Información del Vuelo",
            {
                "fields": (
                    "tipo",
                    "codigo_preview",
                    "origen",
                    "destino",
                )
            },
        ),
        (
            "Horarios",
            {
                "fields": (
                    "fecha_salida",
                    "hora_salida",
                    "fecha_llegada",
                    "hora_llegada",
                    "tiempo_vuelo",
                )
            },
        ),
        (
            "Detalles",
            {
                "fields": (
                    "capacidad",
                    "precio",
                )
            },
        ),
    )

    class Media:
        js = ("aerolinea/js/agregar_vuelo.js",)

    def codigo_preview(self, obj=None):
        if obj and getattr(obj, "codigo", None):
            val = obj.codigo
        else:
            val = "Seleccione un tipo"
        return format_html(
            '<input type="text" id="id_codigo_preview" value="{}" readonly style="background:var(--body-bg, #eee); color:var(--body-fg, #000); border:1px solid var(--border-color, #ccc); padding:2px 4px; width:250px;" />',
            val,
        )

    codigo_preview.short_description = "Código"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "next_codigo/",
                self.admin_site.admin_view(self.next_codigo_view),
                name="next_codigo",
            ),
            path(
                "get_options/",
                self.admin_site.admin_view(self.get_options_view),
                name="get_options",
            ),
            path(
                "calcular_tiempo_vuelo/",
                self.admin_site.admin_view(self.calcular_tiempo_vuelo_view),
                name="calcular_tiempo_vuelo",
            ),
        ]
        return custom_urls + urls

    def next_codigo_view(self, request):

        tipo = request.GET.get("tipo")
        if tipo == "NACIONAL":
            prefix = "VN"
        else:
            prefix = "VI"
        last = (
            Vuelo.objects.filter(tipo=tipo, codigo__startswith=prefix)
            .order_by("-codigo")
            .first()
        )
        if last and last.codigo[2:].isdigit():
            next_num = int(last.codigo[2:]) + 1
        else:
            next_num = 1
        codigo = f"{prefix}{next_num:04d}"
        return JsonResponse({"codigo": codigo})

    def get_options_view(self, request):
        """Vista para obtener las opciones de origen y destino según el tipo de vuelo"""
        tipo = request.GET.get("tipo")
        
        if tipo == "NACIONAL":
            origen_options = Vuelo.VUELOS_NACIONALES
            destino_options = Vuelo.VUELOS_NACIONALES
        elif tipo == "INTERNACIONAL":
            origen_options = Vuelo.ORIGEN_INTERNACIONAL
            destino_options = Vuelo.DESTINO_INTERNACIONAL
        else:
            origen_options = []
            destino_options = []
        
        return JsonResponse({
            "origen_options": origen_options,
            "destino_options": destino_options
        })

    def calcular_tiempo_vuelo_view(self, request):
        """Vista para calcular el tiempo de vuelo basado en origen, destino y tipo"""
        origen = request.GET.get("origen")
        destino = request.GET.get("destino")
        tipo = request.GET.get("tipo")
        fecha_salida = request.GET.get("fecha_salida")
        hora_salida = request.GET.get("hora_salida")
        
        if not all([origen, destino, tipo, fecha_salida, hora_salida]):
            return JsonResponse({"error": "Faltan parámetros requeridos"}, status=400)
        
        try:
            from .models import Capital, calcular_distancia_haversine, ZONAS_HORARIAS_DESTINOS, ZONA_HORARIA_COLOMBIA
            from datetime import datetime, timedelta, time
            import pytz
            
            # Obtener coordenadas
            origen_capital = Capital.objects.get(nombre=origen)
            destino_capital = Capital.objects.get(nombre=destino)
            
            # Calcular distancia
            distancia = calcular_distancia_haversine(
                origen_capital.lat, origen_capital.lon,
                destino_capital.lat, destino_capital.lon
            )
            
            # Velocidad según tipo (usando las mismas velocidades del modelo)
            if tipo == "NACIONAL":
                velocidad = 600  # Airbus A320 km/h
            else:  # INTERNACIONAL
                velocidad = 750  # Airbus A321neo km/h
            
            # Calcular tiempo de vuelo
            tiempo_horas = (distancia / velocidad) + 0.4
            horas = int(tiempo_horas)
            minutos = int((tiempo_horas - horas) * 60)
            tiempo_vuelo = timedelta(hours=horas, minutes=minutos)
            
            # Crear datetime de salida en zona horaria de Colombia
            zona_colombia = pytz.timezone(ZONA_HORARIA_COLOMBIA)
            datetime_salida_local = datetime.strptime(f"{fecha_salida} {hora_salida}", "%Y-%m-%d %H:%M")
            datetime_salida_local = zona_colombia.localize(datetime_salida_local)
            
            # Convertir a UTC para cálculos
            datetime_salida_utc = datetime_salida_local.astimezone(pytz.UTC)
            
            # Calcular datetime de llegada en UTC
            datetime_llegada_utc = datetime_salida_utc + tiempo_vuelo
            
            # Para vuelos internacionales, convertir a hora local del destino
            if tipo == "INTERNACIONAL" and destino in ZONAS_HORARIAS_DESTINOS:
                zona_destino = pytz.timezone(ZONAS_HORARIAS_DESTINOS[destino])
                datetime_llegada_local = datetime_llegada_utc.astimezone(zona_destino)
            else:
                # Para vuelos nacionales, mantener en hora de Colombia
                datetime_llegada_local = datetime_llegada_utc.astimezone(zona_colombia)
            
            return JsonResponse({
                "tiempo_vuelo": f"{horas:02d}:{minutos:02d}",
                "fecha_llegada": datetime_llegada_local.strftime("%Y-%m-%d"),
                "hora_llegada": datetime_llegada_local.strftime("%H:%M"),
                "distancia": round(distancia, 2),
                "velocidad": velocidad
            })
            
        except Capital.DoesNotExist:
            return JsonResponse({"error": "Capital no encontrada"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

@admin.register(Capital)
class CapitalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'lat', 'lon')
    search_fields = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    form = VueloAdminForm
    list_display = ('nombres', 'apellidos', 'email', 'dni', 'rol', 'es_admin')
    search_fields = ('nombres', 'apellidos', 'email', 'dni')
    list_filter = ('rol',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    form = ReservaForm
    list_display = ("id", "usuario", "vuelo", "fecha_reserva", "estado", "num_tiquetes")
    list_filter = ("estado", "fecha_reserva")
    search_fields = ("usuario__nombre",)

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "vuelo", "codigo_reserva", "metodo_pago", "estado")
    list_filter = ("estado", "metodo_pago")
    search_fields = ("codigo_reserva", "usuario__nombre")

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ("id", "compra", "asiento")
    search_fields = ("asiento", "compra__codigo_reserva")

@admin.register(Maleta)
class MaletaAdmin(admin.ModelAdmin):
    list_display = ("id", "checkin", "peso", "costo")
    search_fields = ("checkin__id",)

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)
