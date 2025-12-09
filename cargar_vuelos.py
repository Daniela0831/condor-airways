import os
import django
import random
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "condor_airways.settings")
django.setup()

from aerolinea.models import Vuelo

ciudades = [
    "Pereira", "Medellín", "Bogotá", "Cali", "Cartagena",
    "Barranquilla", "Bucaramanga", "Santa Marta", "San Andrés", "Manizales"
]

for i in range(1, 51):
    origen, destino = random.sample(ciudades, 2)  # ciudades distintas
    fecha_salida = timezone.now() + timedelta(days=random.randint(1, 30))
    fecha_llegada = fecha_salida + timedelta(hours=random.randint(1, 3))
    codigo = f"V{i:03}"

    Vuelo.objects.get_or_create(
        codigo=codigo,
        defaults={
            "origen": origen,
            "destino": destino,
            "fecha_salida": fecha_salida,
            "fecha_llegada": fecha_llegada,
            "capacidad": random.randint(50, 200),
            "precio": random.randint(100000, 600000),
        }
    )

print("✅ 50 vuelos aleatorios cargados correctamente")
