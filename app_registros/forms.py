from django import forms
from .models import Productor, Campo, MarcaSenal, Solicitud, TipoSenal

class ProductorForm(forms.ModelForm):
    class Meta:
        model = Productor
        fields = [
            'nombre', 'apellido', 'dni', 'cuit', 'calle', 'campo',
            'localidad', 'municipio', 'departamento', 'provincia',
            'telefono', 'email', 'latitud', 'longitud', 'area_hectareas',
            'estado', 'observaciones'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'dni': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control'}),
            'calle': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Solo lectura
            'campo': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Solo lectura
            'localidad': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Solo lectura
            'municipio': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Solo lectura
            'departamento': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Solo lectura
            'provincia': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Solo lectura
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
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
        """ self.fields['domicilio'].required = True """
        """ self.fields['distrito'].required = True """
        self.fields['localidad'].required = True
        self.fields['latitud'].required = True
        self.fields['longitud'].required = True
        self.fields['estado'].required = True

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
    class Meta:
        model = MarcaSenal
        fields = [
            'productor', 'campo', 'tipo_tramite', 'numero_orden', 'fecha_inscripcion',
            'fecha_vencimiento', 'descripcion_marca', 'imagen_marca', 'tipo_senal',
            'descripcion_senal', 'vacuno', 'caballar', 'mular', 'asnal', 'ovino', 'cabrio',
            'valor_sellado', 'estado', 'observaciones', 'imagen_carnet_frente', 'imagen_carnet_dorso'
        ]
        widgets = {
            'productor': forms.Select(attrs={'class': 'form-control'}),
            'campo': forms.Select(attrs={'class': 'form-control'}),
            'tipo_tramite': forms.Select(attrs={'class': 'form-control'}),
            'numero_orden': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha_inscripcion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion_marca': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tipo_senal': forms.Select(attrs={'class': 'form-control'}),
            'descripcion_senal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vacuno': forms.NumberInput(attrs={'class': 'form-control'}),
            'caballar': forms.NumberInput(attrs={'class': 'form-control'}),
            'mular': forms.NumberInput(attrs={'class': 'form-control'}),
            'asnal': forms.NumberInput(attrs={'class': 'form-control'}),
            'ovino': forms.NumberInput(attrs={'class': 'form-control'}),
            'cabrio': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_sellado': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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