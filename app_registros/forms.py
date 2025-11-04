from django import forms
from .models import Productor, Campo, MarcaSenal, Solicitud, TipoSenal

class ProductorForm(forms.ModelForm):
    class Meta:
        model = Productor
        fields = [
            'nombre', 'apellido', 'dni', 'cuit', 'domicilio', 
            'distrito', 'localidad', 'telefono', 'email',
            'latitud', 'longitud', 'estado', 'observaciones'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.TextInput(attrs={'class': 'form-control'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'distrito': forms.TextInput(attrs={'class': 'form-control'}),
            'localidad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'latitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'longitud': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

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