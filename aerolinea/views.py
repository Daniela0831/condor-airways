from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from aerolinea.models import Vuelo, Reserva, Usuario, Compra, CheckIn, Maleta, Rol, Departamento, Municipio, Tarjeta, Carrito, CarritoItem, Reubicacion, calcular_distancia_haversine, Noticia
from .utils import asignar_asiento_random
from datetime import date, timedelta, datetime
from .forms import RegistroForm, CompletarAdminForm, RootPasswordForm, VueloAdminForm, EditarVueloForm, TarjetaForm, EditarPerfilForm, NoticiaForm
import re
import os
import json
import random
from .models import Vuelo, Reserva, ReservaPasajero
from .forms import ReservaPasajeroForm
from django.forms import modelformset_factory
from decimal import Decimal, InvalidOperation
from .recomendador import MotorRecomendacion



class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["vuelos"] = Vuelo.objects.all()
        return context

    """
        Hacemos login explícito y redirigimos según rol:
        - root (usuario con atributo es_root True) -> root_dashboard
        - admin (usuario con usuario.es_admin True) -> admin (Django)
        - cliente -> buscar_vuelos
    """
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        # Root
        if hasattr(user, "usuario") and getattr(user.usuario, "es_root", False):
            return redirect("root_dashboard")

        # Administrador normal (usa panel de Django)
        if hasattr(user, "usuario") and getattr(user.usuario, "es_admin", False):
            if not user.usuario.registro_completo:
                return redirect("completar_registro_admin")
            return redirect("admin_dashboard")

        # Usuario cliente
        return redirect("buscar_vuelos")
    


# --- ADMINISTRADOR ---

@login_required
def crear_admin(request):
    if not hasattr(request.user, "usuario") or not request.user.usuario.es_root:
        messages.error(request, "Solo el usuario root puede crear administradores.")
        return redirect("buscar_vuelos")

    if request.method == "POST":
        print("Datos recibidos del formulario:",request.POST)
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Crear usuario Django con permisos administrativos
                user = User.objects.create_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"]
                )
                user.is_staff = True
                user.save()

                rol_admin, _ = Rol.objects.get_or_create(nombre="Administrador")

                # Crear el perfil extendido
                Usuario.objects.create(
                    user=user,
                    rol=rol_admin,
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                    nombres=form.cleaned_data["nombres"],
                    apellidos=form.cleaned_data["apellidos"],
                    dni=form.cleaned_data["dni"],
                    pais=form.cleaned_data["pais"],
                    departamento=form.cleaned_data["departamento"],
                    municipio=form.cleaned_data["municipio"],
                    fecha_nacimiento=form.cleaned_data["fecha_nacimiento"],
                    direccion_facturacion=form.cleaned_data["direccion_facturacion"],
                    genero=form.cleaned_data["genero"],
                    imagen_usuario=form.cleaned_data.get("imagen_usuario"),
                    es_admin=True,
                    registro_completo=True
                )

            except Exception as e:
                messages.error(request, f"Error al crear administrador: {e}")
                print("Error creando administrador:", e)

        else:
            messages.error(request, "Formulario inválido. Verifica los campos.")
            print("Errores del formulario:", form.errors)
    else:
        form = RegistroForm()

    return render(request, "root_dashboard.html", {"form": form})

@login_required
def eliminar_admin(request, admin_id):
    """Permite al root eliminar un administrador."""
    if not hasattr(request.user, "usuario") or not request.user.usuario.es_root:
        messages.error(request, "No tienes permiso para realizar esta acción.")
        return redirect("buscar_vuelos")

    try:
        admin_usuario = Usuario.objects.get(id=admin_id, es_admin=True)
        nombre_admin = f"{admin_usuario.nombres} {admin_usuario.apellidos}"
        admin_usuario.user.delete()  # Esto elimina también el User base
        admin_usuario.delete()
        messages.success(request, f"El administrador '{nombre_admin}' fue eliminado correctamente.")
    except Usuario.DoesNotExist:
        messages.error(request, "El administrador no existe o ya fue eliminado.")
    except Exception as e:
        messages.error(request, f"Ocurrió un error al eliminar el administrador: {e}")

    return redirect("root_dashboard")

@login_required
def completar_registro_admin(request):
    """Permite al administrador completar su información personal."""
    # Verificar que el usuario sea admin
    if not hasattr(request.user, "usuario") or not request.user.usuario.es_admin:
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect("buscar_vuelos")

    usuario = request.user.usuario

    # Si ya completó el registro, redirigir al panel admin
    if usuario.registro_completo:
        return redirect("admin_dashboard")

    if request.method == "POST":
        form = CompletarAdminForm(request.POST, request.FILES, instance=usuario)
        print("Datos recibidos:",request.POST)
        if form.is_valid():
            print("Formulario válido")
            usuario = form.save(commit=False)
            usuario.registro_completo = True
            usuario.save()
            print("Usuario actualizado:",usuario.id)
            messages.success(request, "Registro completado correctamente. Ahora puedes acceder al panel de administración.")
            return redirect("admin_dashboard")
        else:
            print("Errores del formulario:",form.errors)
    else:
        form = CompletarAdminForm(instance=usuario)

    return render(request, "completar_registro_admin.html", {"form": form})
    
@login_required
def admin_dashboard(request):
    # Verifica que sea admin
    if not hasattr(request.user, "usuario") or not request.user.usuario.es_admin:
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect("buscar_vuelos")
    
    print("Entrando a admin_dashboard...")

    vuelos = Vuelo.objects.all().order_by("-fecha_salida")

    # Actualizar automáticamente vuelos finalizados
    for vuelo in vuelos:
        fecha_salida_completa = datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
        fecha_salida_completa = timezone.make_aware(fecha_salida_completa)
        if vuelo.estado == "activo" and fecha_salida_completa < timezone.now():
            vuelo.estado = "finalizado"
            vuelo.save(update_fields=["estado"])

    if request.method == "POST":
        print("POST recibido:", request.POST)
        form = VueloAdminForm(request.POST, request.FILES)
        if form.is_valid():
            vuelo = form.save(commit=False)
            print("Tipo de vuelo recibido:", vuelo.tipo)

            # Validación de tiempo mínimo de creación de vuelos
            fecha_salida = vuelo.fecha_salida
            hora_salida = vuelo.hora_salida

            fecha_completa = timezone.make_aware(datetime.combine(fecha_salida,hora_salida))
            ahora = timezone.now()

            # Diferencia en horas
            diferencia = (fecha_completa - ahora).total_seconds()/3600

            if vuelo.tipo == "nacional" and diferencia < 2:
                messages.error(request, "Los vuelos nacionales deben programarse con al menos 2 horas de anticipación.")
                return redirect("admin_dashboard")

            if vuelo.tipo == "internacional" and diferencia < 3:
                messages.error(request, "Los vuelos internacionales deben programarse con al menos 3 horas de anticipación.")
                return redirect("admin_dashboard")

            vuelo.save()
            messages.success(request, f"Vuelo {vuelo.codigo} creado correctamente.")
            return redirect("admin_dashboard")
        else:
            print("Errores del formulario:", form.errors)
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = VueloAdminForm()
        print("Formulario creado correctamente")

    # Listar vuelos creados
    vuelos = Vuelo.objects.exclude(estado="cancelado").order_by("-fecha_salida")
    print(f"Vuelos cargados: {vuelos.count()}")

    return render(request, "admin_dashboard.html", {"form":form,"vuelos":vuelos})


# --- GESTIÓN DE VUELOS ADMIN ---

@login_required
def cancelar_vuelo(request, vuelo_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    if not usuario.es_admin and not usuario.es_root:
        messages.error(request, "Acceso denegado.")
        return redirect("buscar_vuelos")

    vuelo = get_object_or_404(Vuelo, id=vuelo_id)

    # 1. Validar que no haya pasado
    fecha_hora_vuelo = timezone.make_aware(
        datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
    )

    if fecha_hora_vuelo <= timezone.now():
        messages.error(request, "No puedes cancelar un vuelo que ya sucedió.")
        return redirect("admin_dashboard")

    # CONFIRMACIÓN
    if request.method == "POST":
        vuelo.estado = "cancelado"
        vuelo.save(update_fields=["estado"])

        reservas = Reserva.objects.filter(vuelo=vuelo).exclude(estado="cancelada")

        # Marcar reservas como pendientes de reubicación
        for reserva in reservas:
            reserva.estado = "pendiente_reubicacion"
            reserva.save(update_fields=["estado"])

            reubi, created = Reubicacion.objects.get_or_create(
                reserva=reserva,
                vuelo_cancelado=vuelo
            )

            # Enviar correo al comprador con opciones
            comprador_email = reserva.usuario.user.email

            send_mail(
                subject="Vuelo cancelado - Selecciona una opción",
                message=(
                    f"Tu vuelo {vuelo.codigo} ha sido cancelado.\n\n"
                    f"Puedes elegir una de estas opciones:\n"
                    f"👉 Reembolso completo\n"
                    f"👉 Reubicación en otro vuelo disponible\n\n"
                    f"Ingresa a tu cuenta para seleccionar la opción."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[comprador_email],
                fail_silently=True,
            )

            # Notificar a cada pasajero
            for pasajero in reserva.pasajeros.all():
                if pasajero.correo:
                    send_mail(
                        subject="Cancelación de vuelo",
                        message=(
                            f"Hola {pasajero.nombres},\n\n"
                            f"El vuelo {vuelo.codigo} ha sido cancelado.\n"
                            f"El comprador de la reserva decidirá si solicita reembolso "
                            f"o reubicación en otro vuelo.\n\n"
                            f"Cóndor Airways."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[pasajero.correo],
                        fail_silently=True,
                    )

        messages.success(request, "Vuelo cancelado y notificaciones enviadas.")
        return redirect("admin_dashboard")

    return render(request, "confirmar_cancelacion.html", {"vuelo": vuelo})

@login_required
def editar_vuelo(request, vuelo_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    if not usuario.es_admin and not usuario.es_root:
        messages.error(request, "Acceso denegado.")
        return redirect("buscar_vuelos")

    vuelo = get_object_or_404(Vuelo, id=vuelo_id)

    # No se puede editar si ya pasó o está por iniciar
    fecha_salida_completa = datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
    fecha_salida_completa = timezone.make_aware(fecha_salida_completa)

    if fecha_salida_completa <= timezone.now():
        messages.error(request, "No puedes editar un vuelo que ya inició o finalizó.")
        return redirect("admin_dashboard")

    # No se puede editar si ya tiene reservas o compras
    reservas = Reserva.objects.filter(vuelo=vuelo, estado__in=["activa", "confirmada"])
    compras = Compra.objects.filter(vuelo=vuelo, estado__in=["activa", "completada"])

    if reservas.exists() or compras.exists():
        messages.error(request, "No puedes editar este vuelo porque ya tiene tiquetes vendidos.")
        return redirect("admin_dashboard")
    
    # Crear el formulario con la instancia del vuelo
    form = EditarVueloForm(request.POST or None, request.FILES or None, instance=vuelo)

    # Asegurar que los selects de origen/destino se carguen correctamente
    if vuelo.tipo == "NACIONAL":
        form.fields['origen'].choices = [('', 'Seleccione origen')] + Vuelo.VUELOS_NACIONALES
        form.fields['destino'].choices = [('', 'Seleccione destino')] + Vuelo.VUELOS_NACIONALES
    elif vuelo.tipo == "INTERNACIONAL":
        form.fields['origen'].choices = [('', 'Seleccione origen')] + Vuelo.ORIGEN_INTERNACIONAL
        form.fields['destino'].choices = [('', 'Seleccione destino')] + Vuelo.DESTINO_INTERNACIONAL

    if request.method == "POST":
        if form.is_valid():
            vuelo_editado = form.save(commit=False)

            # ✅ sincronizar campos que vienen del template manual
            vuelo_editado.tipo = request.POST.get("tipo")
            vuelo_editado.origen = request.POST.get("origen")
            vuelo_editado.destino = request.POST.get("destino")
            vuelo_editado.precio = request.POST.get("precio")

            vuelo_editado.codigo = vuelo.codigo  # mantener código
            vuelo_editado.save()

            messages.success(request, f"El vuelo {vuelo.codigo} se actualizó correctamente.")
            return redirect("admin_dashboard")

    return render(request, "editar_vuelo.html", {"form": form, "vuelo": vuelo})

@login_required
def finalizar_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    vuelo.estado = "finalizado"
    vuelo.save()
    messages.info(request, f"El vuelo {vuelo.codigo} fue marcado como finalizado.")
    return redirect("admin_dashboard")

@login_required
def reactivar_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    vuelo.estado = "activo"
    vuelo.save()
    messages.success(request, f"El vuelo {vuelo.codigo} fue reactivado correctamente.")
    return redirect("admin_dashboard")



# --- VUELOS ---

@login_required
def next_codigo_vuelo(request):
    tipo = request.GET.get("tipo")

    # Validar tipo
    if tipo not in ["NACIONAL", "INTERNACIONAL"]:
        return JsonResponse({"error": "Tipo inválido"}, status=400)

    prefix = "VN" if tipo == "NACIONAL" else "VI"

    try:
        # Buscar el último vuelo de ese tipo
        last = Vuelo.objects.filter(tipo=tipo, codigo__startswith=prefix).order_by('-codigo').first()

        if last and last.codigo[2:].isdigit():
            next_num = int(last.codigo[2:]) + 1
        else:
            next_num = 1

        nuevo_codigo = f"{prefix}{next_num:04d}"
        print(f"🟢 Generando código dinámico: {nuevo_codigo}")  # para debug en consola

        return JsonResponse({"codigo": nuevo_codigo})

    except Exception as e:
        print("❌ Error generando código:", e)
        return JsonResponse({"error": str(e)}, status=500)

def get_options_vuelo(request):
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

# Función para obtener coordenadas de la ciudad desde JSON
def obtener_coord(ciudad, archivo_json='capitals.json'):
    """Obtiene latitud y longitud de una ciudad usando un archivo JSON."""
    archivo_json = os.path.join(settings.BASE_DIR, 'aerolinea', 'fixtures', 'capitals.json')
    with open(archivo_json, 'r', encoding='utf-8') as f:
        ciudades = json.load(f)
    for c in ciudades:
        if c['nombre'].upper() == ciudad.upper():
            return c['lat'], c['lon']
    return None, None

def calcular_tiempo_vuelo(request):
    tipo = request.GET.get("tipo")
    origen = request.GET.get("origen")
    destino = request.GET.get("destino")
    fecha_salida = request.GET.get("fecha_salida")
    hora_salida = request.GET.get("hora_salida")

    # Validar campos
    if not all([tipo, origen, destino, fecha_salida, hora_salida]):
        return JsonResponse({"error": "Faltan datos para calcular el tiempo de vuelo."}, status=400)

    try:
        # Combinar fecha y hora
        salida = datetime.strptime(f"{fecha_salida} {hora_salida}", "%Y-%m-%d %H:%M")

        # Obtener coordenadas
        lat_origen, lon_origen = obtener_coord(origen)
        lat_destino, lon_destino = obtener_coord(destino)
        if lat_origen is None or lat_destino is None:
            return JsonResponse({"error": "No se pudieron encontrar las coordenadas de las ciudades."}, status=400)

        # Calcular distancia en km
        distancia_km = calcular_distancia_haversine(lat_origen, lon_origen, lat_destino, lon_destino)

        # Velocidad promedio según tipo de vuelo
        if tipo.upper() == "NACIONAL":
            velocidad_kmh = 800
        else:  # internacional
            velocidad_kmh = 900

        # Calcular duración
        horas_vuelo = distancia_km / velocidad_kmh
        duracion = timedelta(hours=horas_vuelo)

        # Calcular hora de llegada
        llegada = salida + duracion

        return JsonResponse({
            "tiempo_vuelo": str(duracion),
            "fecha_llegada": llegada.date().isoformat(),
            "hora_llegada": llegada.time().strftime("%H:%M")
        })

    except Exception as e:
        print("Error en calcular_tiempo_vuelo:", e)
        return JsonResponse({"error": str(e)}, status=500)


# --- ROOT ---

@login_required
def root_dashboard(request):
    if not hasattr(request.user, "usuario") or not request.user.usuario.es_root:
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect("buscar_vuelos")

    # Crear admin desde el panel del root
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Debes ingresar usuario y contraseña.")
            return redirect("root_dashboard")

        # Verificar si ya existe el usuario
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ese nombre de usuario ya existe.")
            return redirect("root_dashboard")

        rol_admin, _ = Rol.objects.get_or_create(nombre="Administrador")

        # Crear usuario base de Django
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Crear perfil de Usuario
        Usuario.objects.create(
            user=user,
            rol=rol_admin,
            email=email,
            password=password,
            nombres="Pendiente",
            apellidos="Pendiente",
            fecha_nacimiento=date(2000,1,1), #Valor temporal
            dni=f"TEMP{user.id}",
            direccion_facturacion="Sin definir",
            genero="O",
            es_admin=True,
            registro_completo=False
        )
        messages.success(request, f"Administrador '{username}' creado correctamente.")
        return redirect("root_dashboard")

    # Mostrar lista de administradores existentes
    administradores = Usuario.objects.filter(es_admin=True)
    return render(request, "root_dashboard.html", {"administradores": administradores})

@login_required
def root_cambiar_password(request):
    # Validar que sea el root real
    if not hasattr(request.user, "usuario") or not request.user.usuario.es_root:
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect("buscar_vuelos")

    if request.method == "POST":
        form = RootPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            #update_session_auth_hash(request, user)  # Mantiene la sesión activa tras cambiar la contraseña
            messages.success(request, "Tu contraseña se ha actualizado correctamente.")
            return redirect("root_dashboard")
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = RootPasswordForm(user=request.user)

    return render(request, "root_cambiar_password.html", {"form": form})



# --- CLIENTE ---

def buscar_vuelos(request):
    limpiar_reservas_vencidas()

    origen = request.GET.get("origen", "")
    destino = request.GET.get("destino", "")
    tipo_trayecto = request.GET.get("tipo_trayecto", "ida")  # 'ida' o 'ida_vuelta'
    fecha_regreso = request.GET.get("fecha_regreso", "")

    # Guardar última búsqueda para recomendaciones
    if request.user.is_authenticated:
        if destino:
            request.session["ultima_busqueda_destino"] = destino
        if origen:
            request.session["ultima_busqueda_origen"] = origen


    vuelos = Vuelo.objects.filter(
        estado="activo",
        fecha_salida__gte=timezone.now().date()
    ).order_by("fecha_salida")

    if origen:
        vuelos = vuelos.filter(origen__icontains=origen)
    if destino:
        vuelos = vuelos.filter(destino__icontains=destino)

    # Si es ida y vuelta y hay fecha_regreso, podemos buscar vuelos de regreso en la plantilla
    vuelos_regreso = None
    if tipo_trayecto == "ida_vuelta" and fecha_regreso:
        vuelos_regreso = Vuelo.objects.filter(
            origen__icontains=destino,
            destino__icontains=origen,
            fecha_salida=fecha_regreso,
            estado="activo"
        ).order_by("hora_salida")

    # Pendientes de decisión por cancelación (para usuario logueado)
    pendientes = None
    if request.user.is_authenticated:
        usuario = getattr(request.user, "usuario", None)
        if usuario:
            pendientes = Reubicacion.objects.filter(reserva__usuario=usuario, estado="pendiente")

    return render(request, "buscar_vuelos.html", {
        "vuelos": vuelos,
        "vuelos_regreso": vuelos_regreso,
        "tipo_trayecto": tipo_trayecto,
        "fecha_regreso": fecha_regreso,
        "pendientes": pendientes,
        "origen": origen,
        "destino": destino,
    })

def obtener_departamentos(request, pais_id):
    departamentos = Departamento.objects.filter(pais_id=pais_id).values("id", "nombre")
    return JsonResponse(list(departamentos), safe=False)

def obtener_municipios(request, departamento_id):
    municipios = Municipio.objects.filter(departamento_id=departamento_id).values("id", "nombre")
    return JsonResponse(list(municipios), safe=False)

@login_required
def listar_pendientes_reubicacion(request):
    usuario = request.user.usuario
    reservas = Reserva.objects.filter(
        usuario=usuario,
        estado="pendiente_reubicacion"
    )
    return render(request, "pendientes_reubicacion.html",{"reservas":reservas})

@login_required(login_url="/accounts/login/")
def reservar_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    tipo_trayecto = request.GET.get("tipo_trayecto", "ida")
    usuario = get_object_or_404(Usuario, user=request.user)

    # --- Número de formularios a mostrar según el parámetro GET ---
    extra = int(request.GET.get("extra", 1))
    extra = min(max(extra, 1), 5)  # mínimo 1, máximo 5 formularios

    ReservaPasajeroFormSet = modelformset_factory(
        ReservaPasajero, form=ReservaPasajeroForm, extra=extra, can_delete=False
    )

    # Validación 1: verificar si el vuelo sale en menos de 2 horas
    fecha_salida_completa = datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
    fecha_salida_completa = timezone.make_aware(fecha_salida_completa)

    if fecha_salida_completa - timezone.now() < timedelta(hours=2):
        messages.error(request, "No puedes reservar este vuelo, faltan menos de 2 horas para la salida.")
        return redirect("buscar_vuelos")

    # VALIDACIÓN 2: verificar si ya tiene una reserva activa para este vuelo
    reserva_existente = Reserva.objects.filter(usuario=usuario, vuelo=vuelo, estado="activa").exists()
    if reserva_existente:
        messages.warning(request, "Ya tienes una reserva activa para este vuelo.")
        return redirect("ver_carrito")

    if request.method == "POST":
        num_tiquetes = int(request.POST.get("num_tiquetes", 1))
        clase = request.POST.get("clase", "economica")
        incluye_maleta = request.POST.get("incluye_maleta") == "on"

        # Validar máximo 5 tiquetes
        if num_tiquetes > 5:
            messages.error(request, "Solo puedes reservar un máximo de 5 tiquetes por vuelo.")
            return redirect("reservar_vuelo", vuelo_id=vuelo.id)

        formset = ReservaPasajeroFormSet(request.POST, queryset=ReservaPasajero.objects.none())

        if formset.is_valid():
            # Revisar edades de todos los pasajeros
            menores = 0
            for form in formset:
                pasajero = form.cleaned_data
                if "fecha_nacimiento" in pasajero and pasajero["fecha_nacimiento"]:
                    edad = (date.today() - pasajero["fecha_nacimiento"]).days // 365
                    if edad < 18:
                        menores += 1

            # Regla: no permitir que viajen solos si todos son menores
            if menores == len(formset.forms):
                messages.error(request, "No se permite que menores de edad viajen sin acompañante adulto.")
                return redirect("reservar_vuelo", vuelo_id=vuelo.id)
               
            # Crear reserva
            reserva = Reserva.objects.create(
                usuario=usuario,
                vuelo=vuelo,
                tipo_trayecto=tipo_trayecto,
                clase=clase,
                num_tiquetes=num_tiquetes,
                incluye_maleta=incluye_maleta,
                reserved_until=timezone.now() + timedelta(hours=24),
                estado="activa",
            )

            if tipo_trayecto == "ida_vuelta":
                request.session["vuelo_ida"] = vuelo.id
                request.session["reserva_ida"] = reserva.id
                return redirect("seleccionar_regreso")

            # Guardar cada pasajero
            for form in formset:
                pasajero = form.save(commit=False)
                pasajero.reserva = reserva
                pasajero.save()

            # Agregar reserva al carrito
            carrito, _ = Carrito.objects.get_or_create(usuario=usuario)

            # Verificar si ya existe un item de este vuelo en el carrito
            item_existente = CarritoItem.objects.filter(carrito=carrito, vuelo=vuelo).first()
           
            if item_existente:
                # Si ya existe, sumamos los nuevos tiquetes
                item_existente.cantidad += num_tiquetes
                item_existente.save()
            else:
                # Si no existe, creamos un nuevo item
                CarritoItem.objects.create(
                    carrito=carrito,
                    vuelo=vuelo,
                    reserva=reserva,
                    cantidad=num_tiquetes
                )

            messages.success(request, f"Reserva creada correctamente. Código: {reserva.codigo_reserva}")
            return render(request, "reserva_confirmada.html", {"reserva": reserva})
        else:
            messages.error(request, "Por favor completa todos los datos de los pasajeros.")
    else:
        formset = ReservaPasajeroFormSet(queryset=ReservaPasajero.objects.none())

    return render(request, "reservar_vuelo.html", {
        "vuelo": vuelo,
        "formset": formset,
    })

@login_required
def cancelar_reserva(request, reserva_id):
    # Obtenemos el usuario extendido y la reserva
    usuario_ext = get_object_or_404(Usuario, user=request.user)
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=usuario_ext)
    vuelo = reserva.vuelo

    # --- Validar tiempo antes de vuelo ---
    fecha_salida_completa = datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
    fecha_salida_completa = timezone.make_aware(fecha_salida_completa)
    tiempo_restante = fecha_salida_completa - timezone.now()

    if tiempo_restante <= timedelta(hours=24):
        messages.error(request, "No puedes cancelar una reserva con menos de 24 horas antes del vuelo.")
        return redirect("ver_historial_compras")

    try:
        # --- Buscar la tarjeta asociada al usuario base ---
        tarjeta = Tarjeta.objects.filter(usuario=request.user).first()
        if not tarjeta:
            messages.error(request, "No se encontró ninguna tarjeta asociada a tu cuenta.")
            return redirect("ver_historial_compras")

        # --- Calcular reembolso ---
        # Aquí asumimos que tienes un campo `monto_total` en Reserva, si no, suma los precios de los tiquetes
        total_reembolso = Decimal(reserva.monto_total if hasattr(reserva, "monto_total") else 0)

        # --- Aplicar reembolso ---
        tarjeta.saldo += total_reembolso
        tarjeta.save(update_fields=["saldo"])

        # --- Actualizar estado de la reserva ---
        reserva.estado = "cancelada"
        reserva.save(update_fields=["estado"])

        messages.success(
            request,
            f"Reserva cancelada correctamente. Se ha reintegrado ${total_reembolso} a tu tarjeta."
        )

    except Exception as e:
        messages.error(request, f"Ocurrió un error al cancelar la reserva: {e}")

    return redirect("ver_historial_compras")

@login_required
def seleccionar_regreso(request):
    reserva_ida_id = request.session.get("reserva_ida")
    if not reserva_ida_id:
        return redirect("buscar_vuelos")

    reserva = Reserva.objects.get(id=reserva_ida_id)

    vuelos_regreso = Vuelo.objects.filter(
        origen=reserva.vuelo.destino,
        destino=reserva.vuelo.origen,
        fecha_salida__gt=reserva.vuelo.fecha_salida,
        estado="activo"
    )

    return render(request, "seleccionar_regreso.html", {
        "reserva": reserva,
        "vuelos": vuelos_regreso
    })

@login_required
def confirmar_regreso(request, vuelo_regreso_id):
    usuario = request.user.usuario

    vuelo_ida_id = request.session.get("vuelo_ida")
    reserva_ida_id = request.session.get("reserva_ida")

    if not vuelo_ida_id or not reserva_ida_id:
        messages.error(request, "No se pudo completar el trayecto ida y vuelta.")
        return redirect("buscar_vuelos")

    vuelo_ida = Vuelo.objects.get(id=vuelo_ida_id)
    vuelo_regreso = Vuelo.objects.get(id=vuelo_regreso_id)

    reserva_ida = Reserva.objects.get(id=reserva_ida_id)

    # Crear reserva de regreso
    reserva_regreso = Reserva.objects.create(
        usuario=usuario,
        vuelo=vuelo_regreso,
        clase=reserva_ida.clase,
        num_tiquetes=reserva_ida.num_tiquetes,
        reserved_until=timezone.now() + timedelta(hours=24),
        estado="activa",
    )

    # Guardar relación ida ↔ regreso
    reserva_ida.vuelo_regreso = vuelo_regreso
    reserva_ida.save()

    # Carrito
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)

    CarritoItem.objects.create(
        carrito=carrito,
        vuelo=vuelo_ida,
        reserva=reserva_ida,
        cantidad=reserva_ida.num_tiquetes
    )

    CarritoItem.objects.create(
        carrito=carrito,
        vuelo=vuelo_regreso,
        reserva=reserva_regreso,
        cantidad=reserva_regreso.num_tiquetes
    )

    # Limpiar sesión
    del request.session["vuelo_ida"]
    del request.session["reserva_ida"]

    messages.success(request, "Trayecto ida y regreso agregado al carrito.")
    return redirect("ver_carrito")

def limpiar_reservas_vencidas():
    ahora = timezone.now()
    reservas_vencidas = Reserva.objects.filter(
        estado="activa", reserved_until__lt=ahora
    )
    for reserva in reservas_vencidas:
        reserva.estado = "expirada"
        reserva.save()

@login_required
def comprar_vuelo(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    usuario = get_object_or_404(Usuario, user=request.user)
    vuelo = reserva.vuelo
    tarjetas = Tarjeta.objects.filter(usuario=request.user)

    if reserva.usuario != usuario:
        messages.error(request, "No tienes permiso para comprar esta reserva.")
        return redirect("buscar_vuelos")

    # --- Restricción: los admins/root no pueden comprar ---
    if usuario.es_admin or usuario.es_root:
        messages.error(request, "Los administradores no pueden realizar compras.")
        return redirect("buscar_vuelos")

    if request.method == "POST":
        tarjeta_id = request.POST.get("tarjeta")

        if not tarjeta_id:
            messages.error(request, "Debes seleccionar una tarjeta para realizar el pago.")
            return redirect("comprar_vuelo", reserva_id=reserva.id)

        tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id, usuario=request.user)

        # --- Validar que el vuelo no haya salido o esté muy próximo ---
        fecha_salida_completa = datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
        fecha_salida_completa = timezone.make_aware(fecha_salida_completa)

        if fecha_salida_completa <= timezone.now():
            messages.error(request, "No puedes comprar un vuelo que ya ha salido.")
            return redirect("buscar_vuelos")

        if fecha_salida_completa - timezone.now() <= timedelta(minutes=30):
            messages.warning(request, "No puedes comprar un vuelo con menos de 30 minutos antes de la salida.")
            return redirect("buscar_vuelos")

        # --- Verificación de saldo ---
        # --- Precio base con promociones ---
        precio_unitario = vuelo.precio

        if vuelo.promocion_activa and usuario.suscrito_promociones:
            precio_unitario = vuelo.precio_final()

        precio_base = precio_unitario * reserva.num_tiquetes

        # Clase
        recargo_clase = Decimal("0")
        if reserva.clase == "primera":
            recargo_clase = precio_base * Decimal("0.30")

        total = precio_base + recargo_clase
        
        if reserva.tipo_trayecto == "ida_vuelta":
            precio_regreso = reserva.vuelo_regreso.precio

            if reserva.vuelo_regreso.promocion_activa and usuario.suscrito_promociones:
                precio_regreso = reserva.vuelo_regreso.precio_final()

            total += precio_regreso * reserva.num_tiquetes
        
        # --- Generar código de reserva único ---
        codigo_reserva = f"R-{timezone.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100,999)}"

        # --- Crear compra ---
        compra = Compra.objects.create(
            usuario=usuario,
            vuelo=vuelo,
            reserva=reserva,
            codigo_reserva=codigo_reserva,
            metodo_pago=f"Tarjeta {tarjeta.tipo}",
            monto_base=precio_base,
            recargo_clase=recargo_clase,
            monto_total=total,
            estado="activa",   
        )

        if not tarjeta.descontar_saldo(total):
            messages.error(request, "Saldo insuficiente o tarjeta inactiva.")
            return redirect("comprar_vuelo", reserva_id=reserva.id)

        # --- Eliminar del carrito ---
        CarritoItem.objects.filter(carrito__usuario=usuario, vuelo=vuelo).delete()

        # --- Asignar asientos ---
        filas = range(1, 31)
        letras = ['A', 'B', 'C', 'D', 'E', 'F']
        pasajeros = reserva.pasajeros.all()

        if pasajeros.exists():
            # Si hay pasajeros, asignar un asiento único a cada uno
            for p in pasajeros:
                asiento_pasajero = f"{random.choice(filas)}{random.choice(letras)}"
                p.asiento = asiento_pasajero
                p.save()

                try:
                    send_mail(
                        subject="Confirmación de tu reserva - Cóndor Airways",
                        message=(
                            f"Hola {p.nombres},\n\n"
                            f"Tu reserva ha sido confirmada para el vuelo {vuelo.origen} → {vuelo.destino}.\n"
                            f"Fecha: {vuelo.fecha_salida} {vuelo.hora_salida}\n"
                            f"Clase: {reserva.clase}\n"
                            f"Asiento asignado: {p.asiento}\n\n"
                            f"Código de reserva: {codigo_reserva}\n\n"
                            f"¡Gracias por volar con nosotros!\n\n"
                            f"Atentamente,\nEl equipo de Cóndor Airways"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[p.correo],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Error enviando correo a {p.nombres}: {e}")

            # Guardar en la reserva el asiento del primer pasajero (para check-in del comprador)
            reserva.asiento_asignado = pasajeros.first().asiento

        else:
            # Si no hay pasajeros, asignar asiento al comprador
            asiento = f"{random.choice(filas)}{random.choice(letras)}"
            reserva.asiento_asignado = asiento

        reserva.estado = "confirmada"
        reserva.save()

        # --- Enviar correo al comprador ---
        try:
            send_mail(
                subject="Confirmación de tu compra - Cóndor Airways",
                message=(
                    f"¡Gracias por tu compra, {usuario.nombres}!\n\n"
                    f"Tu código de reserva es: {codigo_reserva}\n"
                    f"Vuelo: {vuelo.origen} → {vuelo.destino}\n"
                    f"Fecha: {vuelo.fecha_salida} {vuelo.hora_salida}\n"
                    f"Clase: {reserva.clase}\n"
                    f"Asiento asignado: {reserva.asiento_asignado}\n"
                    f"Número de tiquetes: {reserva.num_tiquetes}\n\n"
                    f"Por favor, conserva este código para tu check-in.\n\n"
                    f"¡Gracias por volar con nosotros!\n\n"
                    f"Atentamente,\nEl equipo de Cóndor Airways"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=True,
            )
        except Exception as e:
            print("Error enviando correo al comprador:", e)

        # --- Confirmación visual ---
        messages.success(
            request,
            f"Compra realizada con éxito. Se descontaron ${total} de tu tarjeta. "
            f"Código de reserva: {codigo_reserva}"
        )

        return redirect("checkin_vuelo", compra_id=compra.id)

    # --- Renderizar vista ---
    return render(
        request,
        "comprar_vuelo.html",
        {
            "reserva": reserva,
            "vuelo": vuelo,
            "tarjetas": tarjetas,
        },
    )

@login_required
def cancelar_compra(request, compra_id):
    # Obtenemos el modelo extendido y el de usuario base
    usuario_ext = get_object_or_404(Usuario, user=request.user)
    compra = get_object_or_404(Compra, id=compra_id, usuario=usuario_ext)
    vuelo = compra.vuelo

    # --- Validar tiempo antes de vuelo ---
    fecha_salida_completa = datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
    fecha_salida_completa = timezone.make_aware(fecha_salida_completa)

    tiempo_restante = fecha_salida_completa - timezone.now()
    if tiempo_restante <= timedelta(hours=1):
        messages.error(request, "No puedes cancelar una compra con menos de 1 hora antes del vuelo.")
        return redirect("ver_historial_compras")

    try:
        # --- Buscar la tarjeta asociada al usuario base ---
        tarjeta = Tarjeta.objects.filter(usuario=request.user).first()

        if not tarjeta:
            print("No se encontró tarjeta asociada a:", request.user.username)
            messages.error(request, "No se encontró ninguna tarjeta asociada a tu cuenta.")
            return redirect("ver_historial_compras")

        # --- Calcular reembolso ---
        total_reembolso = Decimal(compra.monto_total)

        # --- Aplicar reembolso ---
        tarjeta.saldo += compra.monto_total
        tarjeta.save(update_fields=["saldo"])

        # --- Actualizar estados ---
        compra.estado = "cancelada"
        compra.save(update_fields=["estado"])

        if hasattr(compra, "reserva") and compra.reserva:
            reserva = compra.reserva
            reserva.estado = "cancelada"
            reserva.save(update_fields=["estado"])

        messages.success(
            request,
            f"Compra cancelada correctamente. Se ha reintegrado ${total_reembolso} a tu tarjeta."
        )

    except Exception as e:
        messages.error(request, f"Ocurrió un error al cancelar la compra: {e}")

    return redirect("ver_historial_compras")

@login_required
def ver_historial_compras(request):
    usuario = get_object_or_404(Usuario, user=request.user)

    compras = Compra.objects.filter(usuario=usuario).select_related("vuelo", "reserva").order_by("-id")
    reservas = Reserva.objects.filter(usuario=usuario).select_related("vuelo").order_by("-id")

    for compra in compras:
        # Flag para ver si hay pasajeros pendientes de check-in
        reserva = compra.reserva
        if reserva:
            compra.pendientes_checkin = reserva.pasajeros.filter(check_in_realizado=False).exists()
        else:
            compra.pendientes_checkin = False

        # Calcular si se pueden cancelar (más de 1 hora antes del vuelo)
        fecha_salida_completa = datetime.combine(compra.vuelo.fecha_salida, compra.vuelo.hora_salida)
        fecha_salida_completa = timezone.make_aware(fecha_salida_completa)
        tiempo_restante = fecha_salida_completa - timezone.now()

        compra.puede_cancelar = tiempo_restante > timedelta(hours=1) and compra.estado == "activa"
        compra.puede_seleccionar_asiento = compra.estado in ["activa", "completada"]

        # NUEVO: permitir cambiar asiento **antes de hacer check-in**
        compra.puede_cambiar_asiento = compra.estado == "activa" and not CheckIn.objects.filter(compra=compra).exists()

    for reserva in reservas:
        fecha_salida_completa = datetime.combine(reserva.vuelo.fecha_salida, reserva.vuelo.hora_salida)
        fecha_salida_completa = timezone.make_aware(fecha_salida_completa)
        tiempo_restante = fecha_salida_completa - timezone.now()
        reserva.puede_cancelar = tiempo_restante > timedelta(hours=24) and reserva.estado == "activa"

    return render(
        request,
        "historial_compras.html",
        {"compras": compras, "reservas": reservas},
    )

@login_required
def perfil_usuario(request):
    usuario = request.user.usuario

    if request.method == "POST":
        form = EditarPerfilForm(request.POST, request.FILES, instance=usuario)

        if form.is_valid():
            usuario_actualizado = form.save(commit=False)

            # ✅ guardar email correctamente
            request.user.email = form.cleaned_data["email"]
            request.user.save()

            usuario_actualizado.save()

            messages.success(request, "✅ Perfil actualizado correctamente")
            return redirect("perfil_usuario")

        else:
            print("❌ ERRORES FORM:", form.errors)

    else:
        form = EditarPerfilForm(instance=usuario)

        if usuario.pais:
            form.fields["departamento"].queryset = Departamento.objects.filter(pais=usuario.pais)

        if usuario.departamento:
            form.fields["municipio"].queryset = Municipio.objects.filter(departamento=usuario.departamento)

    return render(request, "perfil/perfil_usuario.html", {"form": form})

def opciones_cancelacion(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.estado != "pendiente_reubicacion":
        messages.error(request, "Esta reserva no está pendiente de reubicación.")
        return redirect("ver_historial_compras")

    if request.method == "POST":
        opcion = request.POST.get("opcion")

        if opcion == "reembolso":
            return redirect("procesar_reembolso", reserva.id)

        if opcion == "reubicacion":
            return redirect("seleccionar_reubicacion", reserva.id)

    return render(request, "opciones_cancelacion.html", {"reserva": reserva})

def seleccionar_reubicacion(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    reubi = get_object_or_404(Reubicacion, reserva=reserva)

    vuelos_disponibles = Vuelo.objects.filter(
        origen=reserva.vuelo.origen,
        destino=reserva.vuelo.destino,
        fecha_salida__gte=timezone.now(),
        estado="activo"
    ).exclude(id=reserva.vuelo.id)

    if request.method == "POST":
        vuelo_nuevo = get_object_or_404(Vuelo, id=request.POST.get("vuelo"))

        reserva.vuelo = vuelo_nuevo
        reserva.asiento_asignado = None
        reserva.estado = "confirmada"
        reserva.save()

        reubi.vuelo_nuevo = vuelo_nuevo
        reubi.estado = "completada"
        reubi.save()

        # Correo al comprador
        send_mail(
            subject="Reubicación confirmada",
            message=(
                f"Tu reserva ha sido reubicada al vuelo {vuelo_nuevo.codigo}.\n"
                f"Selecciona tu nuevo asiento cuando desees."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[reserva.usuario.user.email],
            fail_silently=True,
        )

        # Correo a cada pasajero
        for pasajero in reserva.pasajeros.all():
            if pasajero.correo:
                send_mail(
                    subject="Has sido reubicado",
                    message=(
                        f"Hola {pasajero.nombres},\n\n"
                        f"Tu vuelo ha sido reubicado al vuelo {vuelo_nuevo.codigo}.\n"
                        f"Por favor revisa tu reserva."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[pasajero.correo],
                    fail_silently=True,
                )

        messages.success(request, "Has sido reubicado correctamente.")
        return redirect("ver_historial_compras")

    return render(request, "seleccionar_reubicacion.html", {
        "reserva": reserva,
        "vuelos": vuelos_disponibles
    })

def procesar_reembolso(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    compra = Compra.objects.filter(
        usuario=reserva.usuario, vuelo=reserva.vuelo
    ).first()

    if not compra:
        messages.error(request, "No se encontró la compra asociada.")
        return redirect("ver_historial_compras")

    # Reembolso
    tarjeta = Tarjeta.objects.filter(usuario=reserva.usuario.user).first()
    if tarjeta and compra:
        tarjeta.saldo += compra.monto_total
        tarjeta.save(update_fields=["saldo"])

    # Cambiar estados
    reserva.estado = "cancelada"
    reserva.asiento_asignado=None
    reserva.save(update_fields=["estado", "asiento_asignado"])

    if compra:
        compra.estado = "reembolsada"
        compra.save(update_fields=["estado"])

    Reubicacion.objects.filter(reserva=reserva).update(estado="finalizada")

    # Notificar al comprador
    send_mail(
        subject="Reembolso completado",
        message=(
            f"Se ha realizado el reembolso correspondiente a tu reserva "
            f"del vuelo cancelado."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[reserva.usuario.user.email],
        fail_silently=True,
    )

    messages.success(request, "Reembolso completado.")
    return redirect("ver_historial_compras")

# Función auxiliar para calcular costo de maleta
def calcular_costo_maleta(peso: Decimal) -> Decimal:
    return Decimal("20000") if peso <= 20 else Decimal("50000")

@login_required
def checkin_vuelo(request, compra_id):
    compra = get_object_or_404(Compra, id=compra_id, usuario__user=request.user)
    usuario = compra.usuario
    reserva = compra.reserva

    if not reserva:
        messages.error(request, "No hay reserva asociada a esta compra.")
        return redirect("buscar_vuelos")

    # Buscar primer pasajero pendiente de check-in
    pasajero = reserva.pasajeros.filter(check_in_realizado=False).first()
    if not pasajero:
        messages.info(request, "Todos los pasajeros de esta reserva ya hicieron check-in.")
        return redirect("ver_historial_compras")

    if request.method == "POST":
        peso_maleta = request.POST.get("peso_maleta")
        costo_maleta = Decimal("0")

        # Crear check-in
        checkin = CheckIn.objects.create(
            compra=compra,
            pasajero=pasajero,
            asiento=pasajero.asiento
        )

        # Procesar maleta
        if peso_maleta:
            try:
                peso = Decimal(peso_maleta)
                costo_maleta = calcular_costo_maleta(peso)
                Maleta.objects.create(
                    checkin=checkin,
                    peso=peso,
                    costo=costo_maleta
                )
            except (InvalidOperation, ValueError):
                messages.error(request, "Peso de maleta inválido.")
                return redirect("checkin_vuelo", compra_id=compra.id)

        # Actualizar pasajero
        pasajero.check_in_realizado = True
        pasajero.save(update_fields=["check_in_realizado"])

        # Actualizar compra y reserva si ya no quedan pasajeros pendientes
        compra.costo_maleta += costo_maleta
        compra.monto_total += costo_maleta
        if not reserva.pasajeros.filter(check_in_realizado=False).exists():
            reserva.check_in_realizado = True
            compra.estado = "checkin"
            reserva.save(update_fields=["check_in_realizado", "estado"])
            compra.save(update_fields=["costo_maleta", "monto_total", "estado"])
        else:
            # Aún quedan pasajeros pendientes
            compra.save(update_fields=["costo_maleta", "monto_total"])

        messages.success(request, f"Check-in realizado para {pasajero.nombres} {pasajero.apellidos}")
        return redirect("checkin_confirmado", checkin_id=checkin.id)

    return render(request, "checkin_vuelo.html", {
        "compra": compra,
        "reserva": reserva,
        "pasajero": pasajero
    })

def checkin_rapido(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo_reserva")
        documento = request.POST.get("documento")
        peso_maleta = request.POST.get("peso_maleta")

        compra = Compra.objects.filter(codigo_reserva=codigo).first()
        if not compra:
            messages.error(request, "Código de reserva inválido.")
            return redirect("checkin_rapido")

        reserva = compra.reserva
        pasajero = reserva.pasajeros.filter(documento=documento).first()
        if not pasajero:
            messages.error(request, "Pasajero no encontrado.")
            return redirect("checkin_rapido")

        if pasajero.check_in_realizado:
            messages.info(request, "Este pasajero ya realizó check-in.")
            return redirect("checkin_confirmado", checkin_id=CheckIn.objects.filter(compra=compra, pasajero=pasajero).first().id)

        costo_maleta = Decimal("0")
        checkin = CheckIn.objects.create(
            compra=compra,
            pasajero=pasajero,
            asiento=pasajero.asiento
        )

        if peso_maleta:
            try:
                peso = Decimal(peso_maleta)
                costo_maleta = calcular_costo_maleta(peso)
                Maleta.objects.create(
                    checkin=checkin,
                    peso=peso,
                    costo=costo_maleta
                )
            except (InvalidOperation, ValueError):
                messages.error(request, "Peso de maleta inválido.")
                return redirect("checkin_rapido")
        
        # Actualizar compra asociada
        compra.costo_maleta += costo_maleta
        compra.monto_total += costo_maleta
        compra.save(update_fields=["costo_maleta", "monto_total"])

        # Marcar pasajero como check-in realizado
        pasajero.check_in_realizado = True
        pasajero.save(update_fields=["check_in_realizado"])

        # Actualizar compra si no hay pasajeros pendientes
        if not reserva.pasajeros.filter(check_in_realizado=False).exists():
            reserva.check_in_realizado = True
            compra.estado = "checkin"
            reserva.save(update_fields=["check_in_realizado", "estado"])
            compra.save(update_fields=["costo_maleta", "monto_total", "estado"])
        else:
            compra.save(update_fields=["costo_maleta", "monto_total"])

        messages.success(request, f"Check-in realizado para {pasajero.nombres} {pasajero.apellidos}")
        return redirect("checkin_confirmado", checkin_id=checkin.id)

    return render(request, "checkin_rapido.html")

@login_required
def checkin_confirmado(request, checkin_id):
    checkin = get_object_or_404(CheckIn, id=checkin_id)
    pasajero = checkin.pasajero
    compra = checkin.compra
    reserva = compra.reserva
    maletas = checkin.maleta_set.all()
    pendientes = reserva.pasajeros.filter(check_in_realizado=False).exists()

    return render(request, "checkin_confirmado.html", {
        "checkin": checkin,
        "pasajero": pasajero,
        "compra": compra,
        "reserva": reserva,
        "maletas": maletas,
        "pendientes": pendientes
    })

@login_required
def obtener_asiento(request):
    codigo = request.GET.get("codigo_reserva", "").strip()
    usuario = get_object_or_404(Usuario, user=request.user)

    try:
        compra = Compra.objects.get(codigo_reserva=codigo, usuario=usuario)
        reserva = Reserva.objects.filter(
            usuario=usuario, vuelo=compra.vuelo, estado__in=["activa", "confirmada"]
        ).first()

        if reserva and reserva.asiento_asignado:
            return JsonResponse({"success": True, "asiento": reserva.asiento_asignado})
        else:
            return JsonResponse({"success": False, "mensaje": "No se encontró asiento asignado."})
    except Compra.DoesNotExist:
        return JsonResponse({"success": False, "mensaje": "Código de reserva inválido."})

@login_required
def tarjetas_usuario(request):
    tarjetas = Tarjeta.objects.filter(usuario=request.user)
    return render(request, 'tarjetas_usuario.html', {'tarjetas': tarjetas})

@login_required
def agregar_tarjeta(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        numero = request.POST.get("numero")
        fecha_vencimiento = request.POST.get("fecha_vencimiento")
        saldo = request.POST.get("saldo")

        if len(numero) != 16 or not numero.isdigit():
            messages.error(request, "El número de tarjeta debe tener 16 dígitos numérico.")
            return redirect("agregar_tarjeta")

        # Validar que el número no esté repetido
        if Tarjeta.objects.filter(numero=numero).exists():
            messages.error(request, "Esta tarjeta ya está registrada en el sistema.")
            return redirect("agregar_tarjeta")   

        if float(saldo)<0:
            messages.error(request, "El saldo inicial no puede ser negativo.")
            return redirect("agregar_tarjeta")

        fecha_v = date.fromisoformat(fecha_vencimiento)
        if fecha_v < date.today():
            messages.error(request, "La tarjeta no puede tener una fecha de vencimiento pasada.")
            return redirect("agregar_tarjeta")

        if not (tipo and numero and fecha_vencimiento and saldo):
            messages.error(request, "Por favor completa todos los campos.")
            return redirect("agregar_tarjeta")

        Tarjeta.objects.create(
            usuario=request.user,
            tipo=tipo,
            numero=numero,
            fecha_vencimiento=fecha_vencimiento,
            saldo=saldo
        )

        messages.success(request, "Tarjeta agregada exitosamente.")
        return redirect("gestionar_tarjetas")

    return render(request, "agregar_tarjeta.html")

@login_required
def seleccionar_asiento(request, compra_id):
    try:
        compra = Compra.objects.get(pk=compra_id, usuario__user=request.user)
    except Compra.DoesNotExist:
        messages.error(request, "La compra no existe.")
        return redirect("ver_historial_compras")

    reserva = compra.reserva
    if not reserva:
        messages.error(request, "Esta compra no tiene una reserva asociada.")
        return redirect("ver_historial_compras")

    # 🔒 Bloquear cambio si ya se hizo check-in
    if reserva.check_in_realizado or compra.estado == "checkin":
        messages.error(request, "No se puede cambiar el asiento después de realizar el check-in.")
        return redirect("ver_historial_compras")

    # ---- ASIENTOS OCUPADOS ----
    ocupados = set()

    # Otras reservas en el mismo vuelo
    ocupados.update(
        Reserva.objects.filter(vuelo=reserva.vuelo)
        .exclude(id=reserva.id)
        .exclude(asiento_asignado__isnull=True)
        .values_list("asiento_asignado", flat=True)
    )

    # Check-ins
    ocupados.update(
        CheckIn.objects.filter(compra__vuelo=reserva.vuelo)
        .values_list("asiento", flat=True)
    )

    # Pasajeros de otras reservas
    ocupados.update(
        ReservaPasajero.objects.filter(reserva__vuelo=reserva.vuelo)
        .exclude(asiento__isnull=True)
        .values_list("asiento", flat=True)
    )

    # Pasajeros de esta reserva
    pasajeros = reserva.pasajeros.all()

    return render(request, "seleccionar_asiento.html", {
        "compra": compra,
        "reserva": reserva,
        "asientos_ocupados": list(ocupados),
        "pasajeros": pasajeros,
    })

@login_required
def guardar_asiento(request, compra_id):
    if request.method != "POST":
        messages.error(request, "Método inválido.")
        return redirect("ver_historial_compras")

    asiento = request.POST.get("asiento")
    pasajero_id = request.POST.get("pasajero_id")

    if not asiento or not pasajero_id:
        messages.error(request, "No seleccionaste un asiento o pasajero.")
        return redirect("seleccionar_asiento", compra_id=compra_id)

    try:
        compra = Compra.objects.get(pk=compra_id, usuario__user=request.user)
        reserva = compra.reserva
        pasajero = ReservaPasajero.objects.get(pk=pasajero_id, reserva=reserva)
    except (Compra.DoesNotExist, ReservaPasajero.DoesNotExist):
        messages.error(request, "Compra o pasajero no encontrados.")
        return redirect("ver_historial_compras")

    # Verificar si ya cambió
    if pasajero.asiento_cambiado:
        messages.error(request, "Ya has cambiado tu asiento una vez, no puedes cambiarlo nuevamente.")
        return redirect("seleccionar_asiento", compra_id=compra_id)

    # 🔒 Bloquear si ya hizo check-in
    if reserva.check_in_realizado or compra.estado == "checkin":
        messages.error(request, "No se puede cambiar el asiento después de realizar el check-in.")
        return redirect("ver_historial_compras")

    # Actualizar asiento
    pasajero.asiento = asiento
    pasajero.asiento_cambiado = True
    pasajero.save()

    # También actualizar asiento en la reserva principal si es el comprador
    if pasajero.documento == reserva.usuario.dni:
        reserva.asiento_asignado = asiento
        reserva.save()

    # --- Enviar correo de confirmación ---
    try:
        subject = f"Confirmación de cambio de asiento - Reserva {reserva.codigo_reserva}"
        message = (
            f"Hola {pasajero.nombres} {pasajero.apellidos},\n\n"
            f"Se ha realizado un cambio de asiento en tu vuelo.\n\n"
            f"Vuelo: {reserva.vuelo.origen} → {reserva.vuelo.destino}\n"
            f"Fecha salida: {reserva.vuelo.fecha_salida.strftime('%d/%m/%Y')} "
            f"{reserva.vuelo.hora_salida.strftime('%H:%M')}\n"
            f"Asiento asignado: {asiento}\n"
            f"Clase: {reserva.clase}\n"
            f"Trayecto: {reserva.tipo_trayecto}\n\n"
            f"Gracias por viajar con nosotros."
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [pasajero.correo],  # correo del pasajero
            fail_silently=False,
        )
    except Exception as e:
        print("Error enviando correo:", e)
        messages.warning(request, "El asiento se actualizó, pero no se pudo enviar el correo de confirmación.")

    messages.success(request, f"Asiento {asiento} asignado correctamente a {pasajero.nombres} {pasajero.apellidos}.")
    return redirect("ver_historial_compras")

@login_required
def eliminar_tarjeta(request, tarjeta_id):
    tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id, usuario=request.user)

    if Compra.objects.filter(usuario=request.user.usuario, metodo_pago__icontains=tarjeta.numero[-4:], 
    estado='activa').exists():
        messages.error(request, "No puedes eliminar una tarjeta con compras activas.")
        return redirect("gestionar_tarjetas")

    tarjeta.delete()
    messages.success(request, "Tarjeta eliminada correctamente.")
    return redirect('gestionar_tarjetas')

@login_required
def gestionar_tarjetas(request):
    tarjetas = Tarjeta.objects.filter(usuario=request.user)

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        numero = request.POST.get("numero")
        saldo = request.POST.get("saldo")
        fecha_vencimiento = request.POST.get("fecha_vencimiento")

        if not (tipo and numero and saldo and fecha_vencimiento):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("gestionar_tarjetas")

        Tarjeta.objects.create(
            usuario=request.user,
            tipo=tipo,
            numero=numero,
            saldo=saldo,
            fecha_vencimiento=fecha_vencimiento,
        )
        messages.success(request, "Tarjeta agregada correctamente.")
        return redirect("gestionar_tarjetas")

    return render(request, "gestionar_tarjetas.html", {"tarjetas": tarjetas})

def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST, request.FILES)
        print("POST recibido")
        if form.is_valid():
            print("formulario valido")
            # Crear usuario base de Django
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"]
            )

            # Obtener o crear rol
            rol_cliente, _ = Rol.objects.get_or_create(nombre="Cliente")

            # Crear usuario extendido
            Usuario.objects.create(
                user=user,
                rol=rol_cliente,
                email=form.cleaned_data["email"],
                nombres=form.cleaned_data["nombres"],
                apellidos=form.cleaned_data["apellidos"],
                dni=form.cleaned_data["dni"],
                pais = form.cleaned_data["pais"],
                departamento = form.cleaned_data["departamento"],
                municipio = form.cleaned_data["municipio"],
                fecha_nacimiento=form.cleaned_data["fecha_nacimiento"],
                direccion_facturacion=form.cleaned_data["direccion_facturacion"],
                genero=form.cleaned_data["genero"],
                imagen_usuario=form.cleaned_data.get("imagen_usuario")
            )

            messages.success(request, "Usuario registrado correctamente.")
            return redirect("login")
        else:
            # Aquí Django mantiene los datos y errores en el formulario
            print("formulario invalido:",form.errors)
            return render(request, "registro.html", {"form": form})

    else:
        form = RegistroForm()

    return render(request, "registro.html", {"form": form})

def iniciar_sesion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Si el usuario autenticado es el root
            if user.is_superuser and hasattr(user, "usuario") and getattr(user.usuario, "es_root", False):
                login(request, user)
                return redirect("root_dashboard")

            # Si es un administrador normal
            elif hasattr(user, "usuario") and getattr(user.usuario, "es_admin", False):
                login(request, user)
                # Si el admin no ha completado su registro, lo enviamos al formulario
                return redirect("completar_registro_admin")
                messages.success(request, "Tu registro se completó correctamente. Ya puedes inciar sesión.")
                return redirect("login")

            # Si es cliente
            elif hasattr(user, "usuario"):
                login(request, user)
                return redirect("buscar_vuelos")

            else:
                # Caso raro: no tiene perfil extendido
                login(request, user)
                return redirect("buscar_vuelos")

        else:
            messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "registration/login.html")

def cerrar_sesion(request):
    if request.user.is_authenticated:
        # Determinamos el rol antes del logout
        es_admin = (
            request.user.is_staff
            or request.user.is_superuser
            or (hasattr(request.user, "usuario") and request.user.usuario.es_admin)
        )
        logout(request)

        # Redirigimos según rol
        if es_admin:
            return redirect("/accounts/login/") # Panel de Django
        else:
            return redirect("/accounts/login") # Cliente normal
    else:
        return redirect("/accounts/login/")

def noticias(request):
    noticias = Noticia.objects.filter(activa=True)

    if request.user.is_authenticated:
        if not request.user.usuario.suscrito_noticias:
            noticias = noticias.exclude(tipo__in=["PROMO", "ALERTA"])
    else:
        noticias = noticias.exclude(tipo__in=["PROMO", "ALERTA"])

    return render(request, "noticias.html", {
        "noticias": noticias
    })

@login_required
def toggle_suscripcion_noticias(request):
    usuario = request.user.usuario
    usuario.suscrito_noticias = not usuario.suscrito_noticias
    usuario.save()

    messages.success(
        request,
        "✅ Te suscribiste a las noticias"
        if usuario.suscrito_noticias
        else "❌ Cancelaste la suscripción"
    )

    return redirect("noticias")

@login_required
def crear_noticia(request):
    usuario = request.user.usuario

    if not usuario.es_admin and not usuario.es_root:
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect("admin_dashboard")

    if request.method == "POST":
        form = NoticiaForm(request.POST)
        if form.is_valid():
            noticia = form.save(commit=False)
            noticia.creada_por = request.user
            noticia.save()

            messages.success(request, "✅ Noticia creada correctamente")
            return redirect("noticias")
    else:
        form = NoticiaForm()

    return render(request, "crear_noticia.html", {"form": form})

@login_required
def agregar_al_carrito(request, vuelo_id):
    usuario = request.user.usuarios
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)

    item, creado = CarritoItem.objects.get_or_create(carrito=carrito, vuelo=vuelo, defaults={'cantidad': 1})
    if not creado:
        # validar que no supere 5 si al incrementarlo pasa el límite
        if item.cantidad + 1 > 5:
            messages.error(request, "No puedes agregar más de 5 tiquetes por vuelo en el carrito.")
            return redirect("buscar_vuelos")
        item.cantidad += 1
        item.save()
    messages.success(request, "Vuelo agregado al carrito.")
    return redirect("ver_carrito")

@login_required
def ver_carrito(request):
    limpiar_reservas_vencidas()
    usuario = request.user.usuario
    carrito, _ = Carrito.objects.get_or_create(usuario=usuario)
    items = carrito.items.select_related("vuelo")
    total = sum(item.vuelo.precio_final() * item.cantidad for item in carrito.items.all())
    return render(request, "carrito.html", {"carrito": carrito, "items":items, "total":total})

@login_required
def pagar_carrito(request):
    usuario = request.user.usuarios
    carrito = get_object_or_404(Carrito, usuario=usuario)
    tarjetas = Tarjeta.objects.filter(usuario=request.user)

    if request.method == "POST":
        tarjeta_id = request.POST.get("tarjeta")
        if not tarjeta_id:
            messages.error(request, "Debes seleccionar una tarjeta para pagar.")
            return redirect("carrito")

        tarjeta = get_object_or_404(Tarjeta, id=tarjeta_id, usuario=request.user)

        total = sum(
            item.vuelo.precio_final() * item.cantidad
            for item in carrito.items.all()
        )

        if tarjeta.saldo < total:
            messages.error(request, "Saldo insuficiente.")
            return redirect("carrito")

        # Descontar saldo total
        tarjeta.saldo -= total
        tarjeta.save()

        # Crear reservas y compras
        for item in carrito.items.all():
            reserva = Reserva.objects.create(
                usuario=usuario,
                vuelo=item.vuelo,
                num_tiquetes=item.cantidad,
                estado="confirmada"
            )

            codigo_reserva = f"RES{timezone.now().strftime('%Y%m%d')}{reserva.id}"
            Compra.objects.create(
                usuario=usuario,
                vuelo=item.vuelo,
                codigo_reserva=codigo_reserva,
                metodo_pago=f"Tarjeta {tarjeta.tipo}",
                estado="activa"
            )

            # Asignar asiento aleatorio
            fila = random.randint(1, 30)
            letra = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
            reserva.asiento_asignado = f"{fila}{letra}"
            reserva.save()

        # Vaciar el carrito
        carrito.items.all().delete()

        # Enviar correo
        send_mail(
            "Confirmación de compra",
            f"Tu compra fue realizada con éxito. Total: ${total}",
            settings.DEFAULT_FROM_EMAIL,
            [usuario.user.email],
        )

        messages.success(request, f"Compra completada. Total descontado: ${total}")
        return redirect("checkin_vuelo_lista")  # o donde quieras llevarlos después

    return render(request, "pagar_carrito.html", {"carrito": carrito, "tarjetas": tarjetas})

@login_required
def eliminar_del_carrito(request, item_id):
    usuario = get_object_or_404(Usuario, user=request.user)
    carrito_item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=usuario)
    vuelo = carrito_item.vuelo

    fecha_salida_completa = datetime.combine(vuelo.fecha_salida, vuelo.hora_salida)
    fecha_salida_completa = timezone.make_aware(fecha_salida_completa)

    # Validar que falten más de 24 horas para el vuelo
    if fecha_salida_completa - timezone.now() <= timedelta(hours=24):
        messages.error(request, "No puedes cancelar una reserva con menos de 24 horas de anticipación.")
        return redirect("ver_carrito")

    # Si el item tiene una reserva asociada, marcarla como cancelada
    if hasattr(carrito_item, "reserva") and carrito_item.reserva:
        reserva = carrito_item.reserva
        reserva.estado = "cancelada"
        reserva.save(update_fields=["estado"])  # Se guarda en la base de datos

    else:
        # Buscar si hay una reserva del mismo vuelo y usuario activa (por si se perdió la relación)
        reserva = Reserva.objects.filter(
            usuario=usuario,
            vuelo=carrito_item.vuelo,
            estado="activa"
        ).first()
        if reserva:
            reserva.estado = "cancelada"
            reserva.save(update_fields=["estado"])  # Se guarda

    # Eliminar el ítem del carrito
    carrito_item.delete()

    messages.success(request, "La reserva fue eliminada y marcada como cancelada correctamente.")
    return redirect("ver_carrito")

def es_admin(user):
    return hasattr(user, "usuario") and user.usuario.rol.nombre == "Administrador"

@login_required
@user_passes_test(es_admin)
def admin_vuelos(request):
    return render(request, "admin_vuelos.html")

@login_required
@user_passes_test(es_admin)
def admin_usuarios(request):
    return render(request, "admin_usuarios.html")

@login_required
@user_passes_test(es_admin)
def admin_roles(request):
    return render(request, "admin_roles.html")


@login_required
def recomendaciones(request):
    motor = MotorRecomendacion(request.user)

    return render(request, "recomendaciones.html", {
        "recomendados_historial": motor.vuelos_basados_en_historial(),
        "recomendados_busqueda": motor.vuelos_por_ultima_busqueda(),
        "recomendados_tendencias": motor.vuelos_tendencias(),
        "recomendados_baratos": motor.vuelos_baratos(),
        "recomendados_cuando_comprar": motor.cuando_comprar(),
    })
