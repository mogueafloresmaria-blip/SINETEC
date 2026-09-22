from django import forms
from .models import InstitucionConvenio, ConvenioSENA, DocumentoConvenio, BeneficioConvenio


class InstitucionConvenioForm(forms.ModelForm):
    class Meta:
        model = InstitucionConvenio
        fields = [
            'nombre', 'codigo_dane', 'departamento', 'municipio', 'direccion',
            'telefono', 'correo', 'sitio_web', 'nombre_contacto', 'cargo_contacto',
            'telefono_contacto', 'correo_contacto', 'logo', 'descripcion'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. I.E. Técnica Distrital Simón Bolívar'}),
            'codigo_dane': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 147001000123'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control', 'value': 'Magdalena'}),
            'municipio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Santa Marta, Ciénaga, Fundación...'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Calle 22 # 15-40'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. (605) 4210000 o 3001234567'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'contacto@colegio.edu.co'}),
            'sitio_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.colegio.edu.co'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Rector o Coordinador Enlace'}),
            'cargo_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Rector / Coordinador Académico'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono directo de contacto'}),
            'correo_contacto': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'rectoria@colegio.edu.co'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción institucional, sedes, perfil de formación...'}),
        }


class ConvenioSENAForm(forms.ModelForm):
    class Meta:
        model = ConvenioSENA
        fields = [
            'institucion', 'numero_convenio', 'nombre', 'tipo_convenio',
            'descripcion', 'objetivo', 'fecha_inicio', 'fecha_fin',
            'responsable', 'observaciones', 'estado_manual'
        ]
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'numero_convenio': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. CONV-SENA-MAG-2026-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Convenio Marco de Articulación con la Media Técnica'}),
            'tipo_convenio': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Alcance y detalles del convenio...'}),
            'objetivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Objetivo general de la cooperación...'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Funcionario SENA o Enlace Institucional'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observaciones de seguimiento o cláusulas especiales'}),
            'estado_manual': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get('fecha_inicio')
        fin = cleaned_data.get('fecha_fin')
        if inicio and fin and fin <= inicio:
            self.add_error('fecha_fin', 'La fecha de finalización debe ser posterior a la fecha de inicio.')
        return cleaned_data


class DocumentoConvenioForm(forms.ModelForm):
    class Meta:
        model = DocumentoConvenio
        fields = ['nombre', 'tipo', 'archivo', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Minuta del Convenio Firmada 2026'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalles del documento, radicado, folio o acta...'}),
        }


class BeneficioConvenioForm(forms.ModelForm):
    class Meta:
        model = BeneficioConvenio
        fields = ['nombre', 'tipo', 'cantidad_cupos', 'estado', 'fecha_inicio', 'fecha_fin', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Curso Básico de Fundamentos Web'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad_cupos': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Alcance y condiciones del beneficio...'}),
        }

