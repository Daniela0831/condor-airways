# aerolinea/services.py
from django.utils import timezone
from datetime import timedelta
from .models import Reserva, ReservaPasajero, Compra
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import models


MAX_TIQUETES_POR_VUELO = 5
RESERVATION_HOURS = 24

def contar_tiquetes_activas_por_usuario_vuelo(usuario, vuelo):
    """Cuenta tickets activos (compras + reservas activas) del usuario para este vuelo."""
    compras_count = Compra.objects.filter(usuario=usuario, vuelo=vuelo, estado='activa').count()
    reservas_count = Reserva.objects.filter(usuario=usuario, vuelo=vuelo, estado='activa').count()
    # si tus modelos guardan num_tiquetes en Compra o Reserva, sumalos:
    compras_sum = Compra.objects.filter(usuario=usuario, vuelo=vuelo, estado='activa').aggregate(total=models.Sum('cantidad') )['total'] or 0
    reservas_sum = Reserva.objects.filter(usuario=usuario, vuelo=vuelo, estado='activa').aggregate(total=models.Sum('num_tiquetes'))['total'] or 0
    return int(compras_sum + reservas_sum)

def validar_max_tiquetes(usuario, vuelo, nuevos):
    total_actual = contar_tiquetes_activas_por_usuario_vuelo(usuario, vuelo)
    if total_actual + nuevos > MAX_TIQUETES_POR_VUELO:
        raise ValidationError(f"No puedes comprar/reservar más de {MAX_TIQUETES_POR_VUELO} tiquetes por vuelo.")

def validar_pasajeros_no_duplicados_en_vuelo(vuelo, lista_documentos):
    """Verifica que un documento (pasajero) no exista ya como viajero en el mismo vuelo (en compras o reservas activas)."""
    from .models import ReservaPasajero
    # buscar en reservas activas
    duplicados = ReservaPasajero.objects.filter(
        reserva__vuelo=vuelo,
        reserva__estado__in=['activa','confirmada'],
        documento__in=lista_documentos
    ).values_list('documento', flat=True)
    if duplicados:
        raise ValidationError(f"Los siguientes documentos ya están registrados como pasajeros en este vuelo: {', '.join(duplicados)}")
