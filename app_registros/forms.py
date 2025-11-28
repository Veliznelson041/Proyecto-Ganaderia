from django import forms
from .models import Productor, Campo, MarcaSenal, Solicitud, TipoSenal, ImagenMarcaPredefinida
import re
from django.core.validators import RegexValidator


class ProductorForm(forms.ModelForm):
    # Validaciones personalizadas
    dni = forms.CharField(
        max_length=8,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='El DNI debe contener solo números',
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
        max_length=80,
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
            'calle': forms.TextInput(attrs={'class': 'form-control'}),
            'campo': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={
                'class': 'form-control', 
                'required': 'required',
                'pattern': '[A-Za-záéíóúÁÉÍÓÚñÑ\\s]+',
                'title': 'Solo se permiten letras y espacios'
            }),
            'municipio': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'provincia': forms.TextInput(attrs={'class': 'form-control'}),
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
            'area_hectareas': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'estado': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer los campos obligatorios
        self.fields['nombre'].required = True
        self.fields['apellido'].required = True
        self.fields['dni'].required = True
        self.fields['cuit'].required = True
        """ self.fields['domicilio'].required = True """
        """ self.fields['distrito'].required = True """
        self.fields['localidad'].required = True
        self.fields['latitud'].required = True
        self.fields['longitud'].required = True
        self.fields['estado'].required = True

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre:
            # Validar que solo contenga letras y espacios
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', nombre):
                raise forms.ValidationError('El nombre solo puede contener letras y espacios.')
            # Capitalizar nombre
            return nombre.title()
        return nombre
    
    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if apellido:
            # Validar que solo contenga letras y espacios
            if not re.match(r'^[A-Za-záéíóúÁÉÍÓÚñÑ\s]+$', apellido):
                raise forms.ValidationError('El apellido solo puede contener letras y espacios.')
            # Capitalizar apellido
            return apellido.title()
        return apellido
    
    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if dni:
            # Verificar que no exista otro productor con el mismo DNI (excepto si estamos editando)
            if self.instance.pk:
                if Productor.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe un productor con este DNI.')
            else:
                if Productor.objects.filter(dni=dni).exists():
                    raise forms.ValidationError('Ya existe un productor con este DNI.')
        return dni
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Limpiar espacios extras
            telefono = ' '.join(telefono.split())
        return telefono
    
    def clean(self):
        cleaned_data = super().clean()
        latitud = cleaned_data.get('latitud')
        longitud = cleaned_data.get('longitud')
        
        # Validar que se hayan seleccionado coordenadas
        if not latitud or not longitud:
            raise forms.ValidationError('Debe seleccionar una ubicación en el mapa.')
        
        return cleaned_data
    

# ... (los demás forms permanecen igual)

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
            'fecha_inscripcion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion_marca': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'required': 'required'}),
            'imagen_marca': forms.FileInput(attrs={'class': 'form-control'}),
            'tipo_senal': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_senal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vacuno': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'caballar': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'mular': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'asnal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'ovino': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'cabrio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'valor_sellado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'estado': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen_carnet_frente': forms.FileInput(attrs={'class': 'form-control'}),
            'imagen_carnet_dorso': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Filtrar campos según el productor seleccionado
        if 'productor' in self.data:
            try:
                productor_id = int(self.data.get('productor'))
                self.fields['campo'].queryset = Campo.objects.filter(productor_id=productor_id)
            except (ValueError, TypeError):
                self.fields['campo'].queryset = Campo.objects.none()
        elif self.instance.pk and self.instance.productor:
            self.fields['campo'].queryset = self.instance.productor.campos.all()
        else:
            self.fields['campo'].queryset = Campo.objects.none()

        # Ajustar tamaño visual de campos de ganado
        for field in ['vacuno', 'caballar', 'mular', 'asnal', 'ovino', 'cabrio']:
            self.fields[field].widget.attrs.update({'class': 'form-control form-control-sm'})

    def clean_numero_orden(self):
        numero_orden = self.cleaned_data.get('numero_orden')
        if numero_orden:
            if self.instance.pk:
                if MarcaSenal.objects.filter(numero_orden=numero_orden).exclude(pk=self.instance.pk).exists():
                    raise forms.ValidationError('Ya existe una marca/señal con este número de orden.')
            else:
                if MarcaSenal.objects.filter(numero_orden=numero_orden).exists():
                    raise forms.ValidationError('Ya existe una marca/señal con este número de orden.')
        return numero_orden

    def clean_fecha_vencimiento(self):
        fecha_inscripcion = self.cleaned_data.get('fecha_inscripcion')
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        if fecha_vencimiento and fecha_inscripcion:
            if fecha_vencimiento <= fecha_inscripcion:
                raise forms.ValidationError('La fecha de vencimiento debe ser posterior a la fecha de inscripción.')
        return fecha_vencimiento

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