from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from .models import Vuelo, Usuario, Reserva, Pais, Departamento, Municipio, Tarjeta, Noticia
from datetime import date, datetime, timedelta
from django.utils import timezone
import re
from django.forms import modelformset_factory
from .models import ReservaPasajero

class VueloAdminForm(forms.ModelForm):
    codigo_preview = forms.CharField(
        label="Código del vuelo",
        required=False,
        widget=forms.TextInput(attrs={
            "readonly": True,
            "class": "form-control",
            "id": "id_codigo_preview",
        })
    )

    class Meta:
        model = Vuelo
        fields = [
            "tipo",
            "codigo_preview",
            "origen",
            "destino",
            "fecha_salida",
            "hora_salida",
            "fecha_llegada",
            "hora_llegada",
            "tiempo_vuelo",
            "capacidad",
            "precio",
            "imagen",
        ]
        widgets = {
            "fecha_salida": forms.DateInput(attrs={"type": "date"}),
            "hora_salida": forms.TimeInput(attrs={"type": "time"}),
            "fecha_llegada": forms.DateInput(attrs={"type": "date", "readonly": True}),
            "hora_llegada": forms.TimeInput(attrs={"type": "time", "readonly": True}),
            "tiempo_vuelo": forms.TextInput(attrs={"readonly": True}),
            "tipo": forms.Select(attrs={"id": "id_tipo"}),
            "origen": forms.Select(attrs={"id": "id_origen"}),
            "destino": forms.Select(attrs={"id": "id_destino"}),
            "precio": forms.NumberInput(attrs={
                "min": "0", 
                "step": "0.01",
                "placeholder": "0.00"
            }),
            "capacidad": forms.NumberInput(attrs={
                "readonly": True,
                "id": "id_capacidad"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields["codigo_preview"].initial = self.instance.codigo

        # Configurar opciones iniciales para origen y destino
        self.fields['origen'].choices = [('', 'Seleccione el tipo de vuelo')]
        self.fields['destino'].choices = [('', 'Seleccione el tipo de vuelo')]

        tipo = self.data.get("tipo") or (self.instance.tipo if self.instance.pk else None)

        if tipo: 
            if tipo == "NACIONAL":
                self.fields['origen'].choices = [('','Selecciones origen')] + Vuelo.VUELOS_NACIONALES
                self.fields['destino'].choices = [('','Selecciones destino')] + Vuelo.VUELOS_NACIONALES
            elif tipo == "INTERNACIONAL":
                self.fields['origen'].choices = [('','Selecciones origen')] + Vuelo.ORIGEN_INTERNACIONAL
                self.fields['destino'].choices = [('','Selecciones destino')] + Vuelo.DESTINO_INTERNACIONAL
        
        # Si es una edición, establecer las opciones correctas
        elif self.instance and self.instance.pk:
            tipo = self.instance.tipo
            if tipo == "NACIONAL":
                self.fields['origen'].choices = [('', 'Seleccione origen')] + Vuelo.VUELOS_NACIONALES
                self.fields['destino'].choices = [('', 'Seleccione destino')] + Vuelo.VUELOS_NACIONALES
            elif tipo == "INTERNACIONAL":
                self.fields['origen'].choices = [('', 'Seleccione origen')] + Vuelo.ORIGEN_INTERNACIONAL
                self.fields['destino'].choices = [('', 'Seleccione destino')] + Vuelo.DESTINO_INTERNACIONAL

        # Hacer campos de llegada y tiempo de vuelo de solo lectura
        self.fields['fecha_llegada'].widget.attrs['readonly'] = True
        self.fields['hora_llegada'].widget.attrs['readonly'] = True
        self.fields['tiempo_vuelo'].widget.attrs['readonly'] = True

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None:
            # Validar que el precio no sea negativo
            if precio < 0:
                raise ValidationError("El precio no puede ser negativo.")
            
            # Validar que el precio sea numérico (el DecimalField ya hace esto, pero agregamos validación adicional)
            try:
                float(precio)
            except (ValueError, TypeError):
                raise ValidationError("El precio debe ser un número válido.")
        
        return precio

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        origen = cleaned_data.get("origen")
        destino = cleaned_data.get("destino")
        fecha_salida = cleaned_data.get("fecha_salida")
        fecha_llegada = cleaned_data.get("fecha_llegada")
        hora_salida = cleaned_data.get("hora_salida")
        hora_llegada = cleaned_data.get("hora_llegada")
        capacidad = cleaned_data.get("capacidad")
        precio = cleaned_data.get("precio")

        salida = datetime.combine(fecha_salida, hora_salida)
        salida = timezone.make_aware(salida)

        ahora = timezone.now()

        diferencia = salida - ahora

        # NACIONAL : mínimo 2 horas
        if tipo == "NACIONAL" and diferencia < timedelta(hours=2):
            raise forms.ValidationError(
                "Los vuelos nacionales deben crearse con mínimo 2 horas de anticipación."
            )

        # INTERNACIONAL : mínimo 2 horas
        if tipo == "INTERNACIONAL" and diferencia < timedelta(hours=3):
            raise forms.ValidationError(
                "Los vuelos internacionales deben crearse con mínimo 3 horas de anticipación."
            )   
        # Validar salida
        if fecha_salida and hora_salida:
            salida = datetime.combine(fecha_salida, hora_salida)

            # Asegurar que ambas sean aware
            if timezone.is_naive(salida):
                salida = timezone.make_aware(salida, timezone.get_current_timezone())

            ahora = timezone.localtime(timezone.now())

            if salida < (ahora - timedelta(minutes=1)):
                raise ValidationError("La fecha y hora de salida no pueden estar en el pasado.")

        # Validar llegada coherente
        if fecha_llegada and hora_llegada and fecha_salida and hora_salida:
            llegada = datetime.combine(fecha_llegada, hora_llegada)
            if timezone.is_naive(llegada):
                llegada = timezone.make_aware(llegada, timezone.get_current_timezone())

            if llegada <= salida:
                raise ValidationError("La fecha y hora de llegada deben ser posteriores a la salida.")

        if origen and destino and origen == destino:
            raise forms.ValidationError("El origen y el destino no pueden ser iguales.")

        if capacidad is not None and capacidad <= 0:
            raise forms.ValidationError("La capacidad debe ser mayor que 0.")

        if precio is not None and precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que 0.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # 🧠 Si no tiene código, lo generamos antes de guardar
        if not instance.codigo:
            tipo_actual = instance.tipo
            if tipo_actual:
                prefix = "VN" if tipo_actual == "NACIONAL" else "VI"
                last = (
                    Vuelo.objects.filter(codigo__startswith=prefix)
                    .order_by('-codigo')
                    .first()
                )
                next_num = int(last.codigo[2:]) + 1 if last and last.codigo[2:].isdigit() else 1
                instance.codigo = f"{prefix}{next_num:04d}"
                print(f"🟢 Código generado en el form: {instance.codigo}")


        # Guardar si corresponde
        if commit:
            instance.save()
        return instance

class EditarVueloForm(forms.ModelForm):
    class Meta:
        model = Vuelo
        fields = [
            "origen", "destino",
            "fecha_salida", "hora_salida",
            "precio", "promocion_activa", "descuento_porcentaje"
        ]
        widgets = {
            "origen": forms.Select(attrs={"class": "form-select"}),
            "destino": forms.Select(attrs={"class": "form-select"}),
            "fecha_salida": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "hora_salida": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "precio": forms.NumberInput(attrs={"class": "form-control"}),
            "promocion_activa": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "descuento_porcentaje": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100}),
        }

class NoticiaForm(forms.ModelForm):
    class Meta:
        model = Noticia
        fields = [
            "titulo",
            "contenido",
            "tipo",
            "vuelo",
            "descuento_porcentaje",
            "activa",
        ]

    def clean_descuento_porcentaje(self):
        descuento = self.cleaned_data.get("descuento_porcentaje")
        tipo = self.cleaned_data.get("tipo")

        if tipo == "PROMO" and not descuento:
            raise forms.ValidationError(
                "Las promociones deben tener descuento."
            )

        return descuento

class RegistroForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        validators=[RegexValidator(
            r'^[a-zA-Z0-9_]{3,20}$',
            message="El usuario solo puede contener letras, números y guiones bajos (3-20 caracteres)."
        )],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
        error_messages={'required': 'EL CAMPO USUARIO ES OBLIGATORIO'}
    )

    nombres = forms.CharField(
        max_length=150, 
        validators=[RegexValidator(r'^(?! )[A-Za-zÁÉÍÓÚáéíóúÑñ]+(?: [A-Za-zÁÉÍÓÚáéíóúÑñ]+)*(?<! )$',message="Solo letras y un espacio entre palabras.")],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Escribe tus nombres"}),
        error_messages={'required':'EL CAMPO NOMBRES ES OBLIGATORIO'}
    )

    apellidos = forms.CharField(
        max_length=150,
        validators=[RegexValidator(r'^(?! )[A-Za-zÁÉÍÓÚáéíóúÑñ]+(?: [A-Za-zÁÉÍÓÚáéíóúÑñ]+)*(?<! )$',message="Solo letras y un espacio entre palabras.")],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Escribe tus apellidos"}),
        error_messages={'required':'EL CAMPO APELLIDOS ES OBLIGATORIO'}
    )

    email = forms.EmailField(
        validators=[EmailValidator(message="Por favor ingresa un correo válido.")],
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "ejemplo@correo.com"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Contraseña"}),
        error_messages={'required':'EL CAMPO CONTRASEÑA ES OBLIGATORIO'}
    )

    dni = forms.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\d+$',message="El DNI solo puede contener números.")],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Número de documento"}),
        error_messages={'required':'EL CAMPO DNI ES OBLIGATORIO'}
    )

    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        error_messages={'required':'EL CAMPO FECHA DE NACIMIENTO ES OBLIGATORIO'}
    )

    # lugar_nacimiento = forms.CharField(
        #max_length=100,
        #widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Municipio"}),
        #error_messages={'required':'EL CAMPO LUGAR DE NACIMIENTO ES OBLIGATORIO'}
    #)

    pais = forms.ModelChoiceField(
        queryset=Pais.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_pais"})
    )

    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.none(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_departamento"})
    )

    municipio = forms.ModelChoiceField(
        queryset=Municipio.objects.none(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_municipio"})
    )

    direccion_facturacion = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Escribe tu dirección"}),
        error_messages={'required':'EL CAMPO LUGAR DE FACTURACIÓN ES OBLIGATORIO'}
    )

    genero = forms.ChoiceField(
        choices=[("", "Selecciona tu género"), ("M", "Masculino"), ("F", "Femenino"), ("O", "Otro")],
        widget=forms.Select(attrs={"class": "form-select"})
    )

    imagen_usuario = forms.ImageField(required=False)

    class Meta:
        model = Usuario
        fields = [
            "nombres", "apellidos", "dni", "email",
            "fecha_nacimiento", "direccion_facturacion", 
            "genero", "imagen_usuario",
            "pais", "departamento", "municipio"
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "pais": forms.Select(attrs={"class": "form-select", "id": "id_pais"}),
            "departamento": forms.Select(attrs={"class": "form-select", "id": "id_departamento"}),
            "municipio": forms.Select(attrs={"class": "form-select", "id": "id_municipio"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si ya se envió un país, actualizar dinámicamente las opciones
        if 'pais' in self.data:
            try:
                pais_id = int(self.data.get('pais'))
                self.fields['departamento'].queryset = Departamento.objects.filter(pais_id=pais_id)
            except (ValueError, TypeError):
                self.fields['departamento'].queryset = Departamento.objects.none()
        elif self.instance.pk:
            self.fields['departamento'].queryset = Departamento.objects.filter(pais=self.instance.pais)

        # Si ya se envió un departamento, actualizar los municipios
        if 'departamento' in self.data:
            try:
                depto_id = int(self.data.get('departamento'))
                self.fields['municipio'].queryset = Municipio.objects.filter(departamento_id=depto_id)
            except (ValueError, TypeError):
                self.fields['municipio'].queryset = Municipio.objects.none()
        elif self.instance.pk:
            self.fields['municipio'].queryset = Municipio.objects.filter(departamento=self.instance.departamento) 

    # 🔎 Validaciones personalizadas
    def clean_nombres(self):
        nombres = self.cleaned_data.get("nombres", "").strip()
        if not nombres:
            raise forms.ValidationError("El campo nombres no puede estar vacío.")
        return nombres

    def clean_apellidos(self):
        apellidos = self.cleaned_data.get("apellidos", "").strip()
        if not apellidos:
            raise forms.ValidationError("El campo apellidos no puede estar vacío.")
        return apellidos

    def clean_password(self):
        password = self.cleaned_data.get("password", "").strip()
        if len(password) < 6 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres, una letra y un número.")
        return password

    def clean_dni(self):
        dni = self.cleaned_data.get("dni", "").strip()
        if len(dni) < 6 or len(dni) > 15:
            raise forms.ValidationError("El DNI debe tener entre 6 y 15 dígitos.")
        if Usuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("Ya existe un usuario con este DNI.")
        return dni

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        hoy = date.today()
        edad = (hoy - fecha).days // 365
        if fecha > hoy:
            raise forms.ValidationError("La fecha de nacimiento no puede estar en el futuro.")
        if edad < 12:
            raise forms.ValidationError("Debes tener al menos 12 años para registrarte.")
        if edad > 120:
            raise forms.ValidationError("Por favor ingresa una fecha de nacimiento válida.")
        return fecha

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email

    def clean_genero(self):
        genero = self.cleaned_data["genero"]
        if genero == "":
            raise forms.ValidationError("Debes seleccionar un género válido.")
        return genero

    def clean_direccion_facturacion(self):
        direccion = self.cleaned_data["direccion_facturacion"].strip()
        if not direccion:
            raise forms.ValidationError("La dirección de facturación no puede estar vacía.")
        return direccion

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

class EditarPerfilForm(forms.ModelForm):

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Usuario
        fields = [
            "user", "nombres", "apellidos", "dni",
            "email",
            "pais", "departamento", "municipio",
            "fecha_nacimiento",
            "direccion_facturacion",
            "genero",
            "imagen_usuario"
        ]

        widgets = {
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "dni": forms.TextInput(attrs={"class": "form-control"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "direccion_facturacion": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}
            ),
            "pais": forms.Select(attrs={"class": "form-select"}),
            "departamento": forms.Select(attrs={"class": "form-select"}),
            "municipio": forms.Select(attrs={"class": "form-select"}),
            "genero": forms.Select(attrs={"class": "form-select"}),
        }

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'usuario',
            'vuelo',
            'estado',
            'num_tiquetes',
            # Sin fecha_reserva porque se asigna automáticamente
        ]

    def clean(self):
        cleaned_data = super().clean()
        vuelo = cleaned_data.get("vuelo")
        usuario = cleaned_data.get("usuario")

        if vuelo:
            # Validar capacidad
            if vuelo.reserva_set.count() >= vuelo.capacidad:
                raise forms.ValidationError("No quedan asientos disponibles en este vuelo.")

            # Validar duplicados
            if Reserva.objects.filter(vuelo=vuelo, usuario=usuario). exists():
                raise forms.ValidationError("Ya tienes una reserva para este vuelo.")

        return cleaned_data

class ReservaPasajeroForm(forms.ModelForm):
    class Meta:
        model = ReservaPasajero
        fields = [
            'documento','nombres','apellidos','fecha_nacimiento','genero',
            'telefono','correo','contacto_nombre','contacto_telefono'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type':'date'}),
            'genero': forms.Select(choices=[('', 'Seleccione'), ('F','Femenino'), ('M','Masculino'), ('O','Otro')])
        }

    def clean_fecha_nacimiento(self):
        dob = self.cleaned_data.get('fecha_nacimiento')
        if not dob:
            raise ValidationError("Debes ingresar una fecha de nacimiento válida.")

        hoy = date.today()

        # 🔴 No permitir fechas futuras
        if dob > hoy:
            raise ValidationError("La fecha de nacimiento no puede ser en el futuro.")

        # 🔴 No permitir más de 115 años de antigüedad
        edad = hoy.year - dob.year - ((hoy.month, hoy.day) < (dob.month, dob.day))
        if edad > 115:
            raise ValidationError("La edad no puede ser mayor de 115 años.")

        return dob

# Formset para n pasajeros (ajusta extra según UX)
ReservaPasajeroFormSet = modelformset_factory(
    ReservaPasajero,
    form=ReservaPasajeroForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class CompletarAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            "nombres",
            "apellidos",
            "dni",
            "fecha_nacimiento",
            "pais",
            "departamento",
            "municipio",
            "direccion_facturacion",
            "genero",
            "imagen_usuario",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "pais": forms.Select(attrs={"class": "form-select", "id": "id_pais"}),
            "departamento": forms.Select(attrs={"class": "form-select", "id": "id_departamento"}),
            "municipio": forms.Select(attrs={"class": "form-select", "id": "id_municipio"}),
            "direccion_facturacion": forms.TextInput(attrs={"class": "form-control"}),
            "nombres": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "dni": forms.TextInput(attrs={"class": "form-control"}),
            "genero": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cargar dinámicamente los departamentos y municipios
        if "pais" in self.data:
            try:
                pais_id = int(self.data.get("pais"))
                self.fields["departamento"].queryset = Departamento.objects.filter(pais_id=pais_id)
            except (ValueError, TypeError):
                self.fields["departamento"].queryset = Departamento.objects.none()
        elif self.instance.pk and self.instance.pais:
            self.fields["departamento"].queryset = Departamento.objects.filter(pais=self.instance.pais)

        if "departamento" in self.data:
            try:
                dep_id = int(self.data.get("departamento"))
                self.fields["municipio"].queryset = Municipio.objects.filter(departamento_id=dep_id)
            except (ValueError, TypeError):
                self.fields["municipio"].queryset = Municipio.objects.none()
        elif self.instance.pk and self.instance.departamento:
            self.fields["municipio"].queryset = Municipio.objects.filter(departamento=self.instance.departamento)

class RootPasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Ingresa tu contraseña actual"})
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Ingresa la nueva contraseña"})
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirma la nueva contraseña"})
    )

class TarjetaForm(forms.ModelForm):
    class Meta:
        model = Tarjeta
        fields = ['tipo', 'numero', 'nombre_titular', 'fecha_vencimiento', 'cvv', 'saldo']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'tipo': 'Tipo de Tarjeta',
            'numero': 'Número de Tarjeta',
            'nombre_titular': 'Nombre del Titular',
            'fecha_vencimiento': 'Fecha de Vencimiento',
            'cvv': 'CVV',
            'saldo': 'Saldo Disponible',
        }
