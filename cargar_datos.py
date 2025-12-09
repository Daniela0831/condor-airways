import os
import django
import random
from datetime import timedelta
from faker import Faker

# Configuración de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "condor_airways.settings")
django.setup()

from aerolinea.models import (
    Rol, Usuario, Vuelo, Reserva, Compra, CheckIn, Maleta,
    HistorialOperacion, Publicacion, Comentario, Notificacion
)

fake = Faker("es_CO")  # Datos falsos en español de Colombia

def cargar_datos():
    # --- Roles ---
    roles = {}
    for r in ["Cliente", "Administrador", "Root"]:
        roles[r], _ = Rol.objects.get_or_create(nombre=r)

    # --- Usuarios (Clientes) ---
    usuarios = []
    for _ in range(5):
        u, _ = Usuario.objects.get_or_create(
            email=fake.unique.email(),
            defaults={
                "nombre": fake.name(),
                "password": "1234",
                "telefono": fake.phone_number(),
                "direccion": fake.city(),
                "rol": roles["Cliente"]
            }
        )
        usuarios.append(u)

    # --- Usuario Administrador (único) ---
    admin, _ = Usuario.objects.get_or_create(
        email="admin@condor.com",
        defaults={
            "nombre": "Admin Condor",
            "password": "admin123",
            "rol": roles["Administrador"]
        }
    )

    # --- Vuelos ---
    vuelos = []
    ciudades = ["Pereira", "Bogotá", "Medellín", "Cali", "Cartagena"]
    for i in range(5):
        origen, destino = random.sample(ciudades, 2)
        salida = fake.date_time_between(start_date="+1d", end_date="+30d")
        llegada = salida + timedelta(hours=random.randint(1, 3))
        v, _ = Vuelo.objects.get_or_create(
            codigo=f"CO{100+i}",
            defaults={
                "origen": origen,
                "destino": destino,
                "fecha_salida": salida,
                "fecha_llegada": llegada,
                "capacidad": random.randint(80, 200),
                "precio": random.randint(150000, 500000),
            }
        )
        vuelos.append(v)

    # --- Reservas, Compras, CheckIns, Maletas ---
    for u in usuarios:
        vuelo = random.choice(vuelos)
        reserva, _ = Reserva.objects.get_or_create(
            usuario=u,
            vuelo=vuelo,
            defaults={
                "estado": random.choice(["activa", "cancelada", "vencida"]),
                "num_tiquetes": random.randint(1, 3)
            }
        )

        compra, _ = Compra.objects.get_or_create(
            usuario=u,
            vuelo=vuelo,
            defaults={
                "codigo_reserva": f"RES{fake.random_number(digits=5)}",
                "metodo_pago": random.choice(["Tarjeta de Crédito", "PSE", "Efectivo"]),
                "estado": "activa"
            }
        )

        checkin, _ = CheckIn.objects.get_or_create(
            compra=compra,
            defaults={
                "asiento": f"{random.randint(1, 30)}{random.choice(['A','B','C','D'])}"
            }
        )

        Maleta.objects.get_or_create(
            checkin=checkin,
            defaults={
                "peso": round(random.uniform(10, 25), 2),
                "costo": random.randint(20000, 80000)
            }
        )

        # --- Historial de operaciones ---
        HistorialOperacion.objects.create(
            usuario=u,
            tipo=random.choice(["reserva", "compra", "cancelacion", "checkin"]),
            descripcion=fake.sentence(nb_words=8)
        )

        # --- Foro: publicaciones y comentarios ---
        pub = Publicacion.objects.create(
            usuario=u,
            titulo=fake.sentence(nb_words=5),
            contenido=fake.text(max_nb_chars=200)
        )

        for _ in range(random.randint(1, 3)):
            Comentario.objects.create(
                publicacion=pub,
                usuario=random.choice(usuarios),
                contenido=fake.text(max_nb_chars=100)
            )

        # --- Notificaciones ---
        Notificacion.objects.create(
            usuario=u,
            mensaje=fake.sentence(nb_words=10),
            enviada=random.choice([True, False])
        )

    print("✅ Datos de prueba cargados en TODOS los modelos (incluyendo foro, historial y notificaciones).")


if __name__ == "__main__":
    cargar_datos()
