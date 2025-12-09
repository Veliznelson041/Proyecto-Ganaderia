from django import forms
from django.contrib.auth.models import User
from .models import Productor, Campo, MarcaSenal, Solicitud, TipoSenal

class ValidationStyleMixin:
    """
    Mixin para agregar clases CSS de validación (is-valid, is-invalid)
    a los widgets de los campos basándose en el estado de validación.
    """
    def is_valid(self):
        ret = super().is_valid()
        for field_name, field in self.fields.items():
            widget = field.widget
            # Asegurarse de que 'class' esté en attrs
            if 'class' not in widget.attrs:
                widget.attrs['class'] = 'form-control'
            
            # Limpiar clases previas de validación para evitar duplicados si se re-renderiza
            classes = widget.attrs['class'].split()
            classes = [c for c in classes if c not in ['is-valid', 'is-invalid']]
            
            if field_name in self.errors:
                classes.append('is-invalid')
            elif self.data and field_name in self.data and not self.errors.get(field_name):
                # Solo marcar como válido si hay datos y no hay errores
                # Excluir campos vacíos opcionales de ser marcados como verdes
                value = self.cleaned_data.get(field_name)
                if value:
                    classes.append('is-valid')
            
            widget.attrs['class'] = ' '.join(classes)
        return ret

class ProductorForm(ValidationStyleMixin, forms.ModelForm):
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
            'dni': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'maxlength': '8', 'minlength': '8'}),
            'cuit': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '11', 'minlength': '11'}),
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

    def clean_dni(self):
        dni = self.cleaned_data.get('dni')
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if len(dni) != 8:
            raise forms.ValidationError("El DNI debe tener exactamente 8 dígitos.")
        
        # Verificar unicidad si es un nuevo registro
        if not self.instance.pk:
            if Productor.objects.filter(dni=dni).exists():
                raise forms.ValidationError("Ya existe un productor registrado con este DNI.")
        else:
            # Si es edición, verificar que no pertenezca a otro
            if Productor.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Ya existe otro productor registrado con este DNI.")
        return dni

    def clean_cuit(self):
        cuit = self.cleaned_data.get('cuit')
        if not cuit:
            return cuit
            
        cuit = cuit.replace('-', '').replace(' ', '')
        if not cuit.isdigit():
            raise forms.ValidationError("El CUIT debe contener solo números.")
        if len(cuit) != 11:
            raise forms.ValidationError("El CUIT debe tener 11 dígitos.")
            
        # Validación básica de algoritmo de CUIT
        base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        aux = 0
        for i in range(10):
            aux += int(cuit[i]) * base[i]
        
        aux = 11 - (aux % 11)
        if aux == 11:
            aux = 0
        elif aux == 10:
            aux = 9
            
        if int(cuit[10]) != aux:
            raise forms.ValidationError("El CUIT no es válido (dígito verificador incorrecto).")
            
        return cuit

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

class MarcaSenalForm(ValidationStyleMixin, forms.ModelForm):
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

class SolicitudForm(ValidationStyleMixin, forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = ['productor', 'tipo_tramite', 'marca_senal', 'documento_adjunto', 'observaciones']
        widgets = {
            'productor': forms.Select(attrs={'class': 'form-control'}),
            'tipo_tramite': forms.Select(attrs={'class': 'form-control'}),
            'marca_senal': forms.Select(attrs={'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }