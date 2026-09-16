from django import forms
from .models import InstitucionEducativa


class InstitucionEducativaForm(forms.ModelForm):
    """
    Formulario para registrar o editar Instituciones Educativas en convenio.
    """
    class Meta:
        model = InstitucionEducativa
        fields = [
            'codigo_dane', 'nombre', 'municipio', 'direccion',
            'telefono', 'rector_nombre', 'rector_email', 'enlace_nombre', 'enlace_telefono', 'enlace_email', 'activa'
        ]
        widgets = {
            'codigo_dane': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 147001000123'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo del colegio'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Santa Marta, Ciénaga, Aracataca'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección física de la sede principal'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono fijo o celular'}),
            'rector_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del rector(a)'}),
            'rector_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'rectoria@colegio.edu.co'}),
            'enlace_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del docente enlace'}),
            'enlace_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del docente enlace'}),
            'enlace_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'enlace@colegio.edu.co'}),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
