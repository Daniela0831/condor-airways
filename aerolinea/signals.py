from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from aerolinea.models import Rol, Usuario

@receiver(post_migrate)
def crear_datos_iniciales(sender, **kwargs):
    if sender.name != "aerolinea":
        return

    # Crear roles base
    roles = ["Cliente", "Administrador", "Root"]
    for nombre in roles:
        Rol.objects.get_or_create(nombre=nombre)

    rol_root, _ = Rol.objects.get_or_create(nombre="Root")

    # Crear usuario root si no existe
    if not User.objects.filter(username="root").exists():
        root_user = User.objects.create_superuser(
            username="root",
            email="root@condorairways.com",
            password="root123"
        )
        # Crear perfil Usuario asociado
        Usuario.objects.create(
            user=root_user,
            rol=rol_root,
            email="root@condorairways.com",
            nombres="Root",
            apellidos="System",
            dni="0000000000",
            fecha_nacimiento="2000-01-01",
            genero="O",
            direccion_facturacion="Sistema Central",
            es_admin=False,
            es_root=True
        )
        print("✅ Usuario root creado correctamente.")

