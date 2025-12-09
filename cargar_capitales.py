from django.core.management.base import BaseCommand
from django.conf import settings
import os
import json
from aerolinea.models import Capital


class Command(BaseCommand):
    help = 'Carga/actualiza capitales desde static/data/capitals.json'

    def handle(self, *args, **options):
        # Construir la ruta al archivo JSON
        path = os.path.join(settings.BASE_DIR, 'static', 'data', 'capitals.json')
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'No se encontró el archivo: {path}')
            )
            return
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Error al leer el JSON: {e}')
            )
            return

        created = updated = 0
        for item in data:
            nombre = item.get('ciudad') or item.get('nombre')
            lat = item.get('lat')
            lon = item.get('lon')
            
            if not nombre or lat is None or lon is None:
                self.stdout.write(
                    self.style.WARNING(f'Datos incompletos para: {item}')
                )
                continue
                
            obj, did_create = Capital.objects.update_or_create(
                nombre=nombre,
                defaults={'lat': lat, 'lon': lon}
            )
            if did_create:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(f'Capitales procesadas: {created} creadas, {updated} actualizadas.')
        )