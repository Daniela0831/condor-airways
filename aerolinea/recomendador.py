from django.db.models import Avg, Count
from .models import Vuelo, Reserva, PrecioHistoricoVuelo


class MotorRecomendacion:

    def __init__(self, user, session=None):
        self.user = user
        self.session = session

    # ---------------------------------------------------------
    # Detectar cómo está guardado el usuario en la reserva
    # ---------------------------------------------------------
    def _filtro_usuario(self):
        # Si Reserva.usuario es directamente User
        if Reserva._meta.get_field("usuario").remote_field.model.__name__ == "User":
            return {"usuario": self.user}

        # Si Reserva.usuario es un Perfil con FK user
        return {"usuario__user": self.user}

    # ---------------------------------------------------------
    # 1️⃣ Recomendación basada en historial
    # ---------------------------------------------------------
    def vuelos_basados_en_historial(self):
        historial = Reserva.objects.filter(
            **self._filtro_usuario(),
            vuelo__estado="activo"
        ).order_by("-id")

        if not historial.exists():
            return None

        destinos = {}
        for r in historial:
            destino = r.vuelo.destino
            destinos[destino] = destinos.get(destino, 0) + 1

        top_destino = max(destinos, key=destinos.get)

        return Vuelo.objects.filter(
            destino__nombre__icontains=top_destino.nombre,
            estado="activo"
        ).order_by("precio")[:5]

    # ---------------------------------------------------------
    # 2️⃣ Recomendación según última búsqueda
    # ---------------------------------------------------------
    def vuelos_por_ultima_busqueda(self):
        if not self.session:
            return None

        destino = self.session.get("ultima_busqueda_destino", None)
        if not destino:
            return None

        return Vuelo.objects.filter(
            destino__nombre__icontains=destino,
            estado="activo"
        ).order_by("precio")[:5]

    # ---------------------------------------------------------
    # 3️⃣ Tendencias (más reservados)
    # ---------------------------------------------------------
    def vuelos_tendencias(self):
        return (
            Vuelo.objects.filter(estado="activo")
            .annotate(
                num_reservas=Count("reservas_ida") + Count("reservas_regreso")
            )
            .order_by("-num_reservas")[:5]
        )

    # ---------------------------------------------------------
    # 4️⃣ Vuelos más baratos globales
    # ---------------------------------------------------------
    def vuelos_baratos(self):
        return Vuelo.objects.filter(
            estado="activo"
        ).order_by("precio")[:5]

    # ---------------------------------------------------------
    # 5️⃣ Análisis si es buen momento para comprar
    # ---------------------------------------------------------
    def mejor_momento_compra(self, vuelo):
        precios = PrecioHistoricoVuelo.objects.filter(vuelo=vuelo)

        if not precios.exists():
            return "No hay datos suficientes."

        promedio = precios.aggregate(Avg("precio"))["precio__avg"]

        if vuelo.precio < promedio:
            return (
                f"✔ Buen momento: precio actual ${vuelo.precio} "
                f"está por debajo del promedio ${promedio:.0f}"
            )
        else:
            return (
                f"❌ Espera: precio actual ${vuelo.precio} "
                f"está por encima del promedio ${promedio:.0f}"
            )

    # ---------------------------------------------------------
    # 6️⃣ Recomendación "¿cuándo comprar?"
    # ---------------------------------------------------------
    def cuando_comprar(self):
        vuelos = Vuelo.objects.filter(estado="activo")[:5]
        resultado = []

        for v in vuelos:
            resultado.append({
                "vuelo": v,
                "mensaje": "10% de descuento si compras entre las 11:00 pm a 6:00 am",
            })

        return resultado

    # ---------------------------------------------------------
    # 7️⃣ Motor principal (nunca vacío)
    # ---------------------------------------------------------
    def obtener_recomendaciones(self):
        r1 = self.vuelos_basados_en_historial()
        if r1:
            return {
                "tipo": "Basado en tu historial",
                "vuelos": r1
            }

        r2 = self.vuelos_por_ultima_busqueda()
        if r2:
            return {
                "tipo": "Según tu última búsqueda",
                "vuelos": r2
            }

        r3 = self.vuelos_tendencias()
        if r3:
            return {
                "tipo": "Tendencias",
                "vuelos": r3
            }

        # Siempre habrá esto
        return {
            "tipo": "Vuelos más baratos",
            "vuelos": self.vuelos_baratos()
        }
