import random

PRECIO_MALETA = 20000
RECARGO_PRIMERA_CLASE = 0.30

def asignar_asiento_random(clase, vuelo_tipo):
    """
    Asigna un asiento aleatorio según clase y tipo de vuelo.
    vuelo_tipo: "internacional" o "nacional"
    clase: "Económica" o "Primera Clase"
    """
    
    # Definimos filas según tipo de vuelo
    if vuelo_tipo.lower() == "internacional":
        # 250 pasajeros: 1-50 primera clase, 51-250 económica
        filas_primera = range(1, 50)
        filas_economica = range(51, 250)
    else:  # nacional
        # 150 pasajeros: 1-25 primera clase, 26-150 económica
        filas_primera = range(1, 25)
        filas_economica = range(26, 150)
    
    # Elegir fila según clase
    if clase.lower() == "primera clase":
        fila = random.choice(list(filas_primera))
    else:
        fila = random.choice(list(filas_economica))
    
    # Elegir letra
    letras = ['A','B','C','D','E','F']
    letra = random.choice(letras)
    
    return f"{fila}{letra}"