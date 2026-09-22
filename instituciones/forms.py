from django import forms
from .models import InstitucionEducativa, ContactoInstitucional, ObservacionInstitucional


class InstitucionEducativaForm(forms.ModelForm):
    """
    Formulario para registrar o editar Instituciones Educativas en convenio.
    """
    class Meta:
        model = InstitucionEducativa
        fields = [
            'codigo_dane', 'nombre', 'municipio', 'direccion',
            'telefono', 'correo', 'rector_nombre', 'rector_email',
            'enlace_nombre', 'enlace_telefono', 'enlace_email',
            'activa', 'observaciones'
        ]
        widgets = {
            'codigo_dane': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 147001000123'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del colegio'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Santa Marta, Ciénaga, Aracataca'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección física de la sede principal'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono fijo o celular'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@colegio.edu.co'}),
            'rector_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del rector(a)'}),
            'rector_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'rectoria@colegio.edu.co'}),
            'enlace_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del docente enlace'}),
            'enlace_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del docente enlace'}),
            'enlace_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'enlace@colegio.edu.co'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas institucionales o convenios especiales...'}),
        }


class ContactoInstitucionalForm(forms.ModelForm):
    """
    Formulario para administrar contactos institucionales de colegios articulados.
    """
    class Meta:
        model = ContactoInstitucional
        fields = ['institucion', 'nombre', 'apellido', 'cargo', 'tipo', 'correo', 'telefono', 'estado', 'observaciones']
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Rector, Coordinador Académico'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@institucion.edu.co'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono o celular'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Horarios de atención o detalles...'}),
        }


class ObservacionInstitucionalForm(forms.ModelForm):
    """
    Formulario para registrar observaciones, reuniones, acuerdos y antecedentes de colegios.
    """
    class Meta:
        model = ObservacionInstitucional
        fields = ['institucion', 'convenio', 'titulo', 'tipo', 'prioridad', 'estado', 'fecha', 'fecha_seguimiento', 'descripcion', 'resultado']
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'convenio': forms.Select(attrs={'class': 'form-select'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto o título descriptivo'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_seguimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles de la reunión, acuerdo o hecho...'}),
            'resultado': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Compromisos o conclusiones alcanzadas...'}),
        }

