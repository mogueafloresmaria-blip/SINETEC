from django import forms
from .models import (
    BitacoraSeguimiento,
    SeguimientoAdministrativo,
    EventoCalendario,
    DocumentoAdministrativo
)
from academico.models import Matricula
from instituciones.models import InstitucionEducativa
from convenios.models import ConvenioSENA
from academico.models import ProgramaFormacion


class BitacoraSeguimientoForm(forms.ModelForm):
    """
    Formulario para registrar una visita de seguimiento o bitácora formativa.
    Aplica la regla RN-006 (Compromisos exigen fecha de verificación).
    """
    class Meta:
        model = BitacoraSeguimiento
        fields = [
            'ficha', 'matricula', 'fecha_visita', 'tipo_seguimiento', 'estado',
            'observaciones', 'compromisos', 'fecha_verificacion', 'archivo_adjunto'
        ]
        widgets = {
            'ficha': forms.Select(attrs={'class': 'form-select', 'id': 'select-ficha'}),
            'matricula': forms.Select(attrs={'class': 'form-select', 'id': 'select-matricula'}),
            'fecha_visita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_seguimiento': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Diagnóstico pedagógico, técnico y estado del ambiente...'}),
            'compromisos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Plan de mejora o compromisos acordados (si aplica)...'}),
            'fecha_verificacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        ficha_id = kwargs.pop('ficha_id', None)
        super().__init__(*args, **kwargs)
        if 'estado' in self.fields:
            self.fields['estado'].required = False
            self.fields['estado'].initial = 'Realizado'
        if ficha_id:
            self.fields['ficha'].initial = ficha_id
            self.fields['matricula'].queryset = Matricula.objects.filter(ficha_id=ficha_id)
        elif self.instance and self.instance.pk and self.instance.ficha_id:
            self.fields['matricula'].queryset = Matricula.objects.filter(ficha_id=self.instance.ficha_id)
        else:
            self.fields['matricula'].queryset = Matricula.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('estado'):
            cleaned_data['estado'] = 'Realizado'
        compromisos = cleaned_data.get('compromisos')
        fecha_verificacion = cleaned_data.get('fecha_verificacion')
        if compromisos and not fecha_verificacion:
            self.add_error('fecha_verificacion', 'Si registra compromisos, debe indicar una fecha de verificación (RN-006).')
        return cleaned_data


class SeguimientoAdministrativoForm(forms.ModelForm):
    """
    Formulario para crear y editar seguimientos administrativos institucionales.
    """
    class Meta:
        model = SeguimientoAdministrativo
        fields = [
            'institucion', 'convenio', 'asunto', 'descripcion', 'prioridad',
            'estado', 'fecha', 'fecha_limite', 'proxima_accion', 'resultado'
        ]
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'convenio': forms.Select(attrs={'class': 'form-select'}),
            'asunto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Asunto o tarea administrativa'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Detalles de la gestión requerida...'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proxima_accion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acción inmediata a ejecutar'}),
            'resultado': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Logro o resultado alcanzado...'}),
        }


class EventoCalendarioForm(forms.ModelForm):
    """
    Formulario para agendar eventos, reuniones, visitas y vencimientos institucionales.
    """
    class Meta:
        model = EventoCalendario
        fields = ['titulo', 'tipo_evento', 'fecha', 'hora', 'institucion', 'convenio', 'descripcion', 'estado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del evento o reunión'}),
            'tipo_evento': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'convenio': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Agenda, temario o participantes...'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }


class DocumentoAdministrativoForm(forms.ModelForm):
    """
    Formulario para subir y clasificar documentos administrativos al repositorio digital.
    """
    class Meta:
        model = DocumentoAdministrativo
        fields = ['institucion', 'convenio', 'programa', 'nombre', 'tipo', 'archivo', 'descripcion', 'fecha_documento']
        widgets = {
            'institucion': forms.Select(attrs={'class': 'form-select'}),
            'convenio': forms.Select(attrs={'class': 'form-select'}),
            'programa': forms.Select(attrs={'class': 'form-select'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre descriptivo del documento'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Descripción del contenido o validez...'}),
            'fecha_documento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
