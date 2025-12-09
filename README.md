# Proyecto Condor Airways

Este instructivo guía paso a paso la configuración, instalación y ejecución del proyecto **Condor Airways**.

---

## 1. Requisitos

Asegúrate de tener instalados los siguientes componentes:

- [Python](https://www.python.org/) (versión recomendada: 3.10+)
- [Django](https://www.djangoproject.com/)
- [MariaDB](https://mariadb.org/)
- [HeidiSQL](https://www.heidisql.com/) (opcional pero recomendado para la administración de la base de datos)
- Conector de Python para MariaDB: `mysqlclient`

---

## 2. Instalación de dependencias

### a. Crear y activar un entorno virtual
Dentro de la carpeta raíz del proyecto:

```bash
python -m venv venv
```

Activar el entorno virtual:

- En Windows:
```bash
venv\Scripts\activate
```

- En Linux/Mac:
```bash
source venv/bin/activate
```

### b. Instalar dependencias del proyecto
```bash
pip install -r requirements.txt
```

---

## 3. Creación y configuración de la base de datos

### a. Configurar sesión en HeidiSQL
1. Abrir HeidiSQL.
2. Crear una **nueva sesión** con los siguientes datos:
   - Hostname/IP: `127.0.0.1`
   - Usuario: `root`
   - Contraseña: *tu contraseña de MariaDB*
   - Puerto: `3306`
3. Conectarse y crear una nueva base de datos (por ejemplo: `condor_airways`).
4. Verificar que la base de datos aparece en el panel lateral de HeidiSQL.

---

## 4. Configuración de Django

En el archivo `settings.py` del proyecto, modifica la sección `DATABASES` con los datos de tu instalación local:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'condor_airways',  # Nombre de tu base de datos en MariaDB
        'USER': 'root',            # Usuario de MariaDB
        'PASSWORD': '0622',        # Tu contraseña de MariaDB
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

---

## 5. Migraciones y carga inicial de datos

Ejecuta los siguientes pasos en orden:

### a. Cambia al directorio del proyecto
```bash
cd condor_airways
```

### b. Aplicar migraciones iniciales
```bash
python manage.py migrate
```

### c. Cargar capitales
Ejecuta el comando de gestión personalizado:

```bash
python manage.py cargar_capitales
```

### d. Crear superusuario
```bash
python manage.py createsuperuser
```

---

## 6. Prueba de conexión

### a. Levantar el servidor de desarrollo
```bash
python manage.py runserver
```

### b. Verificar acceso en el navegador
- Página principal: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Panel de administración: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 7. Notas finales
- Cada vez que actualices el proyecto o dependencias, recuerda ejecutar:
```bash
pip install -r requirements.txt
```
- Para migraciones futuras:
```bash
python manage.py makemigrations
python manage.py migrate
```
- Mantén el entorno virtual activado durante todo el trabajo con el proyecto.

---

## Flujo rápido de instalación
```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Migraciones y carga inicial
cd condor_airways
python manage.py migrate
python cargar_datos.py
python manage.py cargar_capitales
python manage.py createsuperuser

# 4. Levantar servidor
python manage.py runserver
```
