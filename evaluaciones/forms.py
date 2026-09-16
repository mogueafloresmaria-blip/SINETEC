from django import forms
from .models import JuicioEvaluativo


class JuicioEvaluativoForm(forms.ModelForm):
    """
    Formulario para calificar un resultado de aprendizaje a un aprendiz.
    """
    class Meta:
        model = JuicioEvaluativo
        fields = ['juicio_valor', 'observaciones', 'fecha_evaluacion']
        widgets = {
            'juicio_valor': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Retroalimentación pedagógica...'}),
            'fecha_evaluacion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
