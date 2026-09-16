from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import PerfilUsuario


class LoginForm(AuthenticationForm):
    """
    Formulario de autenticación personalizado con estilos de Bootstrap 5.
    """
    username = forms.CharField(
        label="Usuario o Documento",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej. admin o número de cédula',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingrese su contraseña segura',
        })
    )


class EstudianteForm(forms.Form):
    tipo_documento = forms.ChoiceField(choices=PerfilUsuario.TIPO_DOC_CHOICES, label='Tipo de documento')
    numero_documento = forms.CharField(max_length=20, label='Número de documento')
    nombres = forms.CharField(max_length=150, label='Nombres')
    apellidos = forms.CharField(max_length=150, label='Apellidos')
    correo = forms.EmailField(label='Correo electrónico')
    telefono = forms.CharField(max_length=20, required=False, label='Teléfono')

    def __init__(self, *args, estudiante=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.estudiante = estudiante
        if estudiante is not None and not self.is_bound:
            self.initial.update({
                'tipo_documento': estudiante.tipo_documento,
                'numero_documento': estudiante.numero_documento,
                'nombres': estudiante.usuario.first_name,
                'apellidos': estudiante.usuario.last_name,
                'correo': estudiante.usuario.email,
                'telefono': estudiante.telefono or '',
            })
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['tipo_documento'].widget.attrs['class'] = 'form-select'

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data['numero_documento'].strip()
        consulta = PerfilUsuario.objects.filter(numero_documento=numero_documento)
        if self.estudiante is not None:
            consulta = consulta.exclude(pk=self.estudiante.pk)
        if consulta.exists():
            raise forms.ValidationError('Ya existe un usuario con este número de documento.')
        return numero_documento

    def save(self):
        if self.estudiante is None:
            raise ValueError('El formulario requiere un estudiante existente.')
        self.estudiante.tipo_documento = self.cleaned_data['tipo_documento']
        self.estudiante.numero_documento = self.cleaned_data['numero_documento']
        self.estudiante.telefono = self.cleaned_data['telefono']
        self.estudiante.usuario.first_name = self.cleaned_data['nombres']
        self.estudiante.usuario.last_name = self.cleaned_data['apellidos']
        self.estudiante.usuario.email = self.cleaned_data['correo']
        self.estudiante.usuario.save(update_fields=['first_name', 'last_name', 'email'])
        self.estudiante.save(update_fields=['tipo_documento', 'numero_documento', 'telefono'])
        return self.estudiante


class ImportarEstudiantesExcelForm(forms.Form):
    archivo = forms.FileField(
        label='Archivo Excel de aprendices',
        help_text='Formato permitido: .xlsx',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx',
        }),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']
        if not archivo.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('El archivo debe tener formato .xlsx.')
        if archivo.size > 5 * 1024 * 1024:
            raise forms.ValidationError('El archivo no puede superar los 5 MB.')
        return archivo
