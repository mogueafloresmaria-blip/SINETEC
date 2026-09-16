from django.contrib import admin
from .models import JuicioEvaluativo


@admin.register(JuicioEvaluativo)
class JuicioEvaluativoAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'resultado_aprendizaje', 'juicio_valor', 'instructor', 'fecha_evaluacion')
    list_filter = ('juicio_valor', 'fecha_evaluacion', 'matricula__ficha__institucion', 'matricula__ficha')
    search_fields = (
        'matricula__aprendiz__first_name',
        'matricula__aprendiz__last_name',
        'matricula__aprendiz__username',
        'resultado_aprendizaje__codigo',
        'resultado_aprendizaje__descripcion'
    )
