from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import re

from .models import (
    Productor, Campo, MarcaSenal, Solicitud,
    TipoSenal, ImagenMarcaPredefinida
)

# ============================================================
# Mixin para estilos de validación Bootstrap
# ============================================================

class ValidationStyleMixin:
    """
    Mixin para agregar clases CSS de validación (is-valid, is-invalid)
    a los widgets de los campos basándose en el estado de validación.
    """
    def is_valid(self):
        ret = super().is_valid()
        for field_name, field in self.fields.items():
            widget = field.widget
            if 'class' not in widget.attrs:
                widget.attrs['class'] = 'form-control'

            classes = widget.attrs['class'].split()
            classes = [c for c in classes if c not in ['is-valid', 'is-invalid']]

            if field_name in self.errors:
                classes.append('is-invalid')
            elif self.data and field_name in self.data:
                value = self.cleaned_data.get(field_name)
                if value:
                    classes.append('is-valid')

            widget.attrs['class'] = ' '.join(classes)

        return ret


# ============================================================
# FORM PRODUCTOR
# ============================================================

class ProductorForm(ValidationStyleMixin, forms.ModelForm):

    # Validaciones personalizadas
    dni = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='El DNI debe contener solo números.',
                code='invalid_dni'
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
    )

    cuit = forms.CharField(
        required=False,
        max_length=11,
        validators=[
            RegexValidator(
                regex=r'^\d{2}-\d{8}-\d{1}$',
                message='El CUIT debe tener el formato: 00-00000000-0',
                code='invalid_cuit'
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono = forms.CharField(
        required=False,
        validators=[
            RegexValidator(
                regex=r'^[\d\s\-\+\(\)]+$',
                message='El teléfono solo puede contener números, espacios, y los caracteres: - + ( )',
                code='invalid_phone'
            )
        ],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Productor
        fields = [
            'nombre', 'apellido', 'dni', 'cuit', 'calle', 'campo',
            'localidad', 'municipio', 'departamento', 'provincia',
            'telefono', 'email', 'latitud', 'longitud', 'area_hectareas',
            'estado', 'observaciones'
        ]

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+',
                'title': 'Solo se permiten letras y espacios'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+',
                'title': 'Solo se permiten letras y espacios'
            }),
            'calle': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'campo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'localidad': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+',
                'title': 'Solo se permiten letras y espacios'
            }),
            'municipio': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),

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

            'area_hectareas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # ------------------------
    # VALIDACIONES PERSONALIZADAS
    # ------------------------

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre and not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', nombre):
            raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
        return nombre.title()

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido and not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', apellido):
            raise forms.ValidationError('El apellido solo puede contener letras y espacios.')
        return apellido.title()

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')

        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")

        if len(dni) != 8:
            raise forms.ValidationError("El DNI debe tener exactamente 8 dígitos.")

        # Unicidad
        qs = Productor.objects.filter(dni=dni)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ya existe un productor registrado con este DNI.")

        return dni

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            return ' '.join(telefono.split())
        return telefono

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("latitud") or not cleaned_data.get("longitud"):
            raise forms.ValidationError("Debe seleccionar una ubicación en el mapa.")

        return cleaned_data

    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit')
        if not cuit:
            return cuit

        cuit = cuit.replace('-', '').replace(' ', '')
        if not cuit.isdigit():
            raise forms.ValidationError("El CUIT debe contener solo números.")
        if len(cuit) != 11:
            raise forms.ValidationError("El CUIT debe tener 11 dígitos.")

        # Validación del dígito verificador
        base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        aux = sum(int(cuit[i]) * base[i] for i in range(10))
        aux = 11 - (aux % 11)
        aux = 0 if aux == 11 else (9 if aux == 10 else aux)

        if int(cuit[10]) != aux:
            raise forms.ValidationError("El CUIT no es válido (dígito verificador incorrecto).")

        return cuit


# ============================================================
# FORM CAMPO
# ============================================================

class CampoForm(ValidationStyleMixin, forms.ModelForm):
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


# ============================================================
# FORM MARCA SEÑAL
# ============================================================

class MarcaSenalForm(forms.ModelForm):

    imagen_predefinida = forms.ModelChoiceField(
        queryset=ImagenMarcaPredefinida.objects.filter(activa=True),
        required=False,
        label="Seleccionar marca predefinida",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = MarcaSenal
        fields = [
            'productor', 'campo', 'tipo_tramite', 'numero_orden', 'fecha_inscripcion',
            'fecha_vencimiento', 'descripcion_marca', 'imagen_marca', 'imagen_predefinida',
            'tipo_senal', 'descripcion_senal', 'vacuno', 'caballar', 'mular', 'asnal',
            'ovino', 'cabrio', 'valor_sellado', 'estado', 'observaciones',
            'imagen_carnet_frente', 'imagen_carnet_dorso'
        ]
        widgets = {
            'productor': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'campo': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'tipo_tramite': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'numero_orden': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fecha_inscripcion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion_marca': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen_marca': forms.FileInput(attrs={'class': 'form-control'}),
            'tipo_senal': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_senal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vacuno': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'caballar': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'mular': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'asnal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ovino': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'cabrio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valor_sellado': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen_carnet_frente': forms.FileInput(attrs={'class': 'form-control'}),
            'imagen_carnet_dorso': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar campos según el productor elegido
        if 'productor' in self.data:
            try:
                productor_id = int(self.data.get('productor'))
                self.fields['campo'].queryset = Campo.objects.filter(productor_id=productor_id)
            except:
                self.fields['campo'].queryset = Campo.objects.none()

        elif self.instance.pk and self.instance.productor:
            self.fields['campo'].queryset = self.instance.productor.campos.all()

        else:
            self.fields['campo'].queryset = Campo.objects.none()

        # Tamaño reducido para campos de ganado
        for f in ['vacuno', 'caballar', 'mular', 'asnal', 'ovino', 'cabrio']:
            self.fields[f].widget.attrs.update({'class': 'form-control form-control-sm'})

    def clean_numero_orden(self):
        num = self.cleaned_data.get('numero_orden')
        qs = MarcaSenal.objects.filter(numero_orden=num)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError('Ya existe una marca/señal con este número de orden.')

        return num

    def clean_fecha_vencimiento(self):
        fi = self.cleaned_data.get('fecha_inscripcion')
        fv = self.cleaned_data.get('fecha_vencimiento')

        if fv and fi and fv <= fi:
            raise forms.ValidationError("La fecha de vencimiento debe ser posterior a la inscripción.")

        return fv


# ============================================================
# FORM SOLICITUD
# ============================================================

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
