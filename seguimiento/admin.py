from django.contrib import admin
from .models import AsistenciaAprendiz, BitacoraSeguimiento


@admin.register(AsistenciaAprendiz)
class AsistenciaAprendizAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'matricula', 'estado', 'registrado_por')
    list_filter = ('estado', 'fecha', 'matricula__ficha')
    search_fields = ('matricula__aprendiz__first_name', 'matricula__aprendiz__last_name', 'matricula__aprendiz__perfil__numero_documento')
    date_hierarchy = 'fecha'


@admin.register(BitacoraSeguimiento)
class BitacoraSeguimientoAdmin(admin.ModelAdmin):
    list_display = ('fecha_visita', 'ficha', 'matricula', 'tipo_seguimiento', 'instructor', 'tiene_compromisos', 'fecha_verificacion')
    list_filter = ('tipo_seguimiento', 'fecha_visita', 'ficha__institucion')
    search_fields = ('ficha__codigo_ficha', 'matricula__aprendiz__first_name', 'matricula__aprendiz__last_name', 'observaciones', 'compromisos')
    date_hierarchy = 'fecha_visita'

    def tiene_compromisos(self, obj):
        return bool(obj.compromisos)
    tiene_compromisos.boolean = True
    tiene_compromisos.short_description = "¿Tiene Compromisos?"
