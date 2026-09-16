from django import forms
from django.contrib.auth.models import User
from .models import Ficha, Matricula
from usuarios.models import PerfilUsuario


class FichaForm(forms.ModelForm):
    """
    Formulario para la apertura y asignación de Fichas de Media Técnica.
    """
    class Meta:
        model = Ficha
        fields = ['codigo_ficha', 'programa', 'institucion', 'instructor_lider', 'fecha_inicio', 'fecha_fin', 'estado']
        widgets = {
            'codigo_ficha': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 2501234'}),
            'programa': forms.Select(attrs={'class': 'form-select'}),
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'instructor_lider': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class MatriculaRapidaForm(forms.Form):
    """
    Formulario ergonómico que permite registrar un nuevo aprendiz y matricularlo
    en la ficha técnica en una sola operación.
    """
    TIPO_DOC_CHOICES = [
        ('TI', 'Tarjeta de Identidad'),
        ('CC', 'Cédula de Ciudadanía'),
        ('PEP', 'Permiso Especial de Permanencia'),
        ('PPT', 'Permiso por Protección Temporal'),
    ]
    GRADOS_ESCOLARES = [
        ('10', 'Grado 10° (Décimo)'),
        ('11', 'Grado 11° (Undécimo)'),
    ]

    tipo_documento = forms.ChoiceField(choices=TIPO_DOC_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    numero_documento = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de documento'}))
    nombres = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres completos'}))
    apellidos = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos completos'}))
    correo = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}))
    telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Celular o teléfono'}))
    grado_escolar = forms.ChoiceField(choices=GRADOS_ESCOLARES, widget=forms.Select(attrs={'class': 'form-select'}))
    acudiente_nombre = forms.CharField(max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del acudiente'}))
    acudiente_telefono = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del acudiente'}))


class ImportarAprendicesForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo de aprendices',
        help_text='Formatos permitidos: .xlsx o .csv. El archivo debe incluir encabezados.',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.csv',
        }),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        extension = archivo.name.lower().rsplit('.', 1)[-1] if '.' in archivo.name else ''
        if extension not in {'xlsx', 'csv'}:
            raise forms.ValidationError('El archivo debe tener formato .xlsx o .csv.')
        if archivo.size > 5 * 1024 * 1024:
            raise forms.ValidationError('El archivo no puede superar los 5 MB.')
        return archivo
