from django import forms
from .models import Productor, Campo, MarcaSenal, Solicitud, TipoSenal, ImagenMarcaPredefinida
import re
from django.core.validators import RegexValidator


from django import forms
from django.core.validators import RegexValidator
from .models import Productor
from .validators import (
    DNIValidator, CUITValidator, NombreApellidoValidator,
    TelefonoValidator, EmailValidator
)
import re


class ProductorForm(forms.ModelForm):

    # =========================
    # CAMPOS CON VALIDADORES
    # =========================
    dni = forms.CharField(
        max_length=8,
        validators=[DNIValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'\d{7,8}',
            'title': 'DNI: 7 u 8 números sin puntos ni espacios',
            'placeholder': '12345678'
        })
    )

    cuit = forms.CharField(
        required=False,
        validators=[CUITValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'\d{2}-\d{8}-\d{1}',
            'title': 'Formato: 00-00000000-0',
            'placeholder': '20-12345678-9'
        })
    )

    nombre = forms.CharField(
        validators=[NombreApellidoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Juan'
        })
    )

    apellido = forms.CharField(
        validators=[NombreApellidoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Pérez'
        })
    )

    telefono = forms.CharField(
        required=False,
        max_length=80,
        validators=[TelefonoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'[\d\s\-\+\(\)]+',
            'title': 'Ej: 3511234567, (351) 123-4567'
        })
    )

    email = forms.EmailField(
        required=False,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@ejemplo.com'
        })
    )

    area_hectareas = forms.DecimalField(
        required=False,
        min_value=0,
        max_value=1_000_000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        })
    )

    # =========================
    # META
    # =========================
    class Meta:
        model = Productor
        fields = [
            'nombre', 'apellido', 'dni', 'cuit', 'calle', 'campo',
            'localidad', 'municipio', 'departamento', 'provincia',
            'telefono', 'email', 'latitud', 'longitud',
            'area_hectareas', 'estado', 'observaciones'
        ]
        widgets = {
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'campo': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Catamarca',
                'readonly': 'readonly'
            }),
            'latitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.00000001',
                'required': 'required',
                'readonly': 'readonly'
            }),
            'longitud': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.00000001',
                'required': 'required',
                'readonly': 'readonly'
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
        }

    # =========================
    # INIT
    # =========================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Asegurar clase CSS en todos los campos
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    # =========================
    # LIMPIEZAS
    # =========================
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        return nombre.title() if nombre else nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        return apellido.title() if apellido else apellido

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')

        if dni:
            dni_limpio = re.sub(r'[^\d]', '', str(dni))

            query = Productor.objects.filter(dni__icontains=dni_limpio)
            if self.instance.pk:
                query = query.exclude(pk=self.instance.pk)

            if query.exists():
                raise forms.ValidationError(
                    f'Ya existe un productor con DNI {dni_limpio}.',
                    code='duplicate_dni'
                )

            return dni_limpio

        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            return ' '.join(telefono.split())
        return telefono

    def clean(self):
        cleaned_data = super().clean()
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')

        if not latitud or not longitud:
            raise forms.ValidationError(
                'Debe seleccionar una ubicación en el mapa.'
            )

        # Validación geográfica Argentina
        if latitud < -55 or latitud > -21 or longitud < -75 or longitud > -53:
            raise forms.ValidationError(
                'Las coordenadas deben estar dentro del territorio argentino.'
            )

        return cleaned_data


class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = ['nombre', 'area_hectareas', 'distrito', 'departamento', 'latitud', 'longitud', 'observaciones']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'area_hectareas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'distrito': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


from django import forms
from datetime import date

from .models import (
    MarcaSenal, Campo, TipoSenal, ImagenMarcaPredefinida
)
from .validators import NumeroOrdenValidator


class MarcaSenalForm(forms.ModelForm):

    numero_orden = forms.IntegerField(
        validators=[NumeroOrdenValidator(MarcaSenal)],
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'min': '1',
            'placeholder': '123'
        })
    )

    fecha_inscripcion = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required',
            'max': date.today().isoformat()
        })
    )

    fecha_vencimiento = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': date.today().isoformat()
        })
    )

    descripcion_marca = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'required': 'required',
            'placeholder': 'Describa la marca detalladamente...'
        })
    )

    descripcion_senal = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Describa la señal si aplica...'
        })
    )

    valor_sellado = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0',
            'placeholder': '0.00'
        })
    )

    # Campos de ganado
    def ganado_field():
        return forms.IntegerField(
            required=False,
            min_value=0,
            max_value=100000,
            widget=forms.NumberInput(attrs={
                'class': 'form-control form-control-sm small-input',
                'style': 'max-width: 100px;',
                'value': '0',
                'min': '0'
            })
        )

    vacuno = ganado_field()
    caballar = ganado_field()
    mular = ganado_field()
    asnal = ganado_field()
    ovino = ganado_field()
    cabrio = ganado_field()

    class Meta:
        model = MarcaSenal
        fields = [
            'productor', 'campo', 'tipo_tramite', 'numero_orden',
            'fecha_inscripcion', 'fecha_vencimiento',
            'descripcion_marca', 'imagen_marca', 'imagen_predefinida',
            'tipo_senal', 'descripcion_senal',
            'vacuno', 'caballar', 'mular', 'asnal', 'ovino', 'cabrio',
            'valor_sellado', 'estado', 'observaciones',
            'imagen_carnet_frente', 'imagen_carnet_dorso'
        ]
        widgets = {
            'productor': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'campo': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'tipo_tramite': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'tipo_senal': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen_marca': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_carnet_frente': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_carnet_dorso': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'imagen_predefinida': forms.Select(attrs={
                'class': 'form-control d-done',
                'id': 'id_imagen_predefinida_form'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tipo señal
        self.fields['tipo_senal'].queryset = TipoSenal.objects.all()
        self.fields['tipo_senal'].empty_label = "Seleccione un tipo de señal"

        # Imagen predefinida
        self.fields['imagen_predefinida'].queryset = (
            ImagenMarcaPredefinida.objects.filter(activa=True)
        )
        self.fields['imagen_predefinida'].required = False

        # Filtrar campos por productor
        if 'productor' in self.data:
            try:
                productor_id = int(self.data.get('productor'))
                self.fields['campo'].queryset = Campo.objects.filter(
                    productor_id=productor_id
                )
            except (ValueError, TypeError):
                self.fields['campo'].queryset = Campo.objects.none()
        elif self.instance.pk and self.instance.productor:
            self.fields['campo'].queryset = self.instance.productor.campos.all()
        else:
            self.fields['campo'].queryset = Campo.objects.none()

        # Help text
        self.fields['campo'].help_text = 'Primero seleccione un productor'
        self.fields['valor_sellado'].help_text = 'Valor en pesos argentinos'
        self.fields['descripcion_marca'].help_text = 'Mínimo 10 caracteres'

    def clean_fecha_vencimiento(self):
        fecha_inscripcion = self.cleaned_data.get('fecha_inscripcion')
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')

        if fecha_vencimiento and fecha_inscripcion:
            if fecha_vencimiento <= fecha_inscripcion:
                raise forms.ValidationError(
                    'La fecha de vencimiento debe ser posterior a la fecha de inscripción.'
                )
        return fecha_vencimiento

    def clean(self):
        cleaned_data = super().clean()

        # Validar descripción mínima
        descripcion = cleaned_data.get('descripcion_marca', '')
        if len(descripcion.strip()) < 10:
            self.add_error(
                'descripcion_marca',
                'La descripción debe tener al menos 10 caracteres.'
            )

        # Validar ganado mínimo
        tipos = ['vacuno', 'caballar', 'mular', 'asnal', 'ovino', 'cabrio']
        total = sum(cleaned_data.get(t, 0) or 0 for t in tipos)

        if total <= 0:
            raise forms.ValidationError(
                'Debe especificar al menos un animal.'
            )

        return cleaned_data


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['productor', 'tipo_tramite', 'marca_senal', 'documento_adjunto', 'observaciones']
        widgets = {
            'productor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_tramite': forms.Select(attrs={'class': 'form-control'}),
            'marca_senal': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }