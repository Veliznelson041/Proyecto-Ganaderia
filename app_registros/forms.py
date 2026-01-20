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


import re
from django import forms
from .models import Productor
from .validators import (
    DNIValidator,
    CUITValidator,
    NombreApellidoValidator,
    TelefonoValidator,
    EmailValidator
)


class ProductorForm(forms.ModelForm):

    # =========================
    # CAMPOS PERSONALIZADOS
    # =========================
    dni = forms.CharField(
        max_length=8,
        validators=[DNIValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'\d{7,8}',
            'title': 'DNI: 7 u 8 números sin puntos ni espacios',
            'placeholder': '12345678',
            'oninput': "this.value = this.value.replace(/[^0-9]/g, '')"
        })
    )

    cuit = forms.CharField(
        required=False,
        validators=[CUITValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'\d{2}-\d{8}-\d{1}',
            'title': 'Formato: 00-00000000-0',
            'placeholder': '20-12345678-9',
            'onkeypress': 'return validarCUIT(event, this)',
            'oninput': 'formatearCUIT(this)'
        })
    )

    nombre = forms.CharField(
        validators=[NombreApellidoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Juan',
            'onkeypress': 'return soloLetras(event)',
            'oninput': 'capitalizarPrimeraLetra(this)'
        })
    )

    apellido = forms.CharField(
        validators=[NombreApellidoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'required': 'required',
            'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo letras y espacios',
            'placeholder': 'Pérez',
            'onkeypress': 'return soloLetras(event)',
            'oninput': 'capitalizarPrimeraLetra(this)'
        })
    )

    telefono = forms.CharField(
        required=False,
        max_length=80,
        validators=[TelefonoValidator()],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'[\d\s\-\+\(\)]+',
            'title': 'Ej: 3511234567, (351) 123-4567, +54 351 1234567',
            'placeholder': '3511234567',
            'oninput': 'validarTelefono(this)'
        })
    )

    email = forms.EmailField(
        required=False,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@ejemplo.com',
            'title': 'Ejemplo: usuario@dominio.com',
            'oninput': 'validarEmail(this)'
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
                'required': 'required',
                'pattern': r'[A-Za-záéíóúÁÉÍÓÚñÑ\s]+',
                'title': 'Solo letras y espacios'
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
            dni_limpio = re.sub(r'\D', '', dni)

            qs = Productor.objects.filter(dni=dni_limpio)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError(
                    f'Ya existe un productor con DNI {dni_limpio}.',
                    code='duplicate_dni'
                )

            return dni_limpio

        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        return ' '.join(telefono.split()) if telefono else telefono

    def clean(self):
        cleaned_data = super().clean()
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')

        if not latitud or not longitud:
            raise forms.ValidationError(
                'Debe seleccionar una ubicación en el mapa.'
            )

        # Validación geográfica Argentina
        if not (-55 <= latitud <= -21 and -75 <= longitud <= -53):
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


from django.core.validators import FileExtensionValidator
from datetime import timedelta

class SolicitudForm(forms.ModelForm):
    # Campos con validaciones específicas
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'required': 'required',
            'placeholder': 'Describa el motivo de la solicitud...',
            'minlength': '20',
            'title': 'Mínimo 20 caracteres'
        })
    )
    
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Observaciones adicionales...'
        })
    )
    
    fecha_vencimiento = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    documento_adjunto = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx'
        })
    )
    
    class Meta:
        model = Solicitud
        fields = [
            'productor', 'tipo_tramite', 'marca_senal', 'prioridad', 
            'motivo', 'observaciones', 'documento_adjunto',
            'imagen_adicional_1', 'imagen_adicional_2', 'fecha_vencimiento'
        ]
        widgets = {
            'productor': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'tipo_tramite': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required',
                'onchange': 'toggleMarcaSenal(this)'
            }),
            'marca_senal': forms.Select(attrs={
                'class': 'form-control',
                'disabled': 'disabled'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-control'
            }),
            'imagen_adicional_1': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'imagen_adicional_2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar marcas/señales según el productor seleccionado
        if 'productor' in self.data:
            try:
                productor_id = int(self.data.get('productor'))
                self.fields['marca_senal'].queryset = MarcaSenal.objects.filter(productor_id=productor_id)
            except (ValueError, TypeError):
                self.fields['marca_senal'].queryset = MarcaSenal.objects.none()
        elif self.instance.pk and self.instance.productor:
            self.fields['marca_senal'].queryset = self.instance.productor.marcas_senales.all()
        else:
            self.fields['marca_senal'].queryset = MarcaSenal.objects.none()
        
        # Establecer fecha de vencimiento por defecto (7 días)
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['fecha_vencimiento'].initial = timezone.now() + timedelta(days=7)
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_tramite = cleaned_data.get('tipo_tramite')
        marca_senal = cleaned_data.get('marca_senal')
        
        # Validaciones según el tipo de trámite
        if tipo_tramite in ['RENOVACION', 'TRANSFERENCIA', 'BAJA', 'MODIFICACION']:
            if not marca_senal:
                self.add_error('marca_senal', 'Para este tipo de trámite debe seleccionar una marca/señal.')
        
        # Validar que la fecha de vencimiento sea futura
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')
        if fecha_vencimiento and fecha_vencimiento < timezone.now():
            self.add_error('fecha_vencimiento', 'La fecha de vencimiento debe ser futura.')
        
        # Validar tamaño de archivos
        documento_adjunto = cleaned_data.get('documento_adjunto')
        if documento_adjunto and documento_adjunto.size > 10 * 1024 * 1024:  # 10MB
            self.add_error('documento_adjunto', 'El documento no puede superar los 10MB.')
        
        return cleaned_data
    
    def save(self, commit=True):
        solicitud = super().save(commit=False)
        
        # Asignar el solicitante actual
        if not solicitud.pk:
            solicitud.solicitante = self.user
        
        if commit:
            solicitud.save()
        
        return solicitud


# Formulario para revisión de solicitudes
class SolicitudRevisionForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['estado', 'observaciones_internas', 'fecha_vencimiento']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones_internas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observaciones internas para el revisor...'
            }),
            'fecha_vencimiento': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }