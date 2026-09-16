from django import forms
from .models import BitacoraSeguimiento
from academico.models import Matricula


class BitacoraSeguimientoForm(forms.ModelForm):
    """
    Formulario para registrar una visita de seguimiento o bitácora formativa.
    Aplica la regla RN-006 (Compromisos exigen fecha de verificación).
    """
    class Meta:
        model = BitacoraSeguimiento
        fields = [
            'ficha', 'matricula', 'fecha_visita', 'tipo_seguimiento',
            'observaciones', 'compromisos', 'fecha_verificacion', 'archivo_adjunto'
        ]
        widgets = {
            'ficha': forms.Select(attrs={'class': 'form-select', 'id': 'select-ficha'}),
            'matricula': forms.Select(attrs={'class': 'form-select', 'id': 'select-matricula'}),
            'fecha_visita': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_seguimiento': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Diagnóstico pedagógico, técnico y estado del ambiente...'}),
            'compromisos': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Plan de mejora o compromisos acordados (si aplica)...'}),
            'fecha_verificacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'archivo_adjunto': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        ficha_id = kwargs.pop('ficha_id', None)
        super().__init__(*args, **kwargs)
        if ficha_id:
            self.fields['ficha'].initial = ficha_id
            self.fields['matricula'].queryset = Matricula.objects.filter(ficha_id=ficha_id)
        else:
            self.fields['matricula'].queryset = Matricula.objects.none()
