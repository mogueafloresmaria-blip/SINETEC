from django.contrib import admin
from .models import ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula, HorarioFicha


class CompetenciaInline(admin.TabularInline):
    model = Competencia
    extra = 1


class ResultadoAprendizajeInline(admin.TabularInline):
    model = ResultadoAprendizaje
    extra = 1


@admin.register(ProgramaFormacion)
class ProgramaFormacionAdmin(admin.ModelAdmin):
    list_display = ('codigo_programa', 'denominacion', 'version', 'activo')
    list_filter = ('activo',)
    search_fields = ('codigo_programa', 'denominacion')
    inlines = [CompetenciaInline]


@admin.register(Competencia)
class CompetenciaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion_corta', 'programa')
    list_filter = ('programa',)
    search_fields = ('codigo', 'descripcion')
    inlines = [ResultadoAprendizajeInline]

    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + "..." if len(obj.descripcion) > 60 else obj.descripcion
    descripcion_corta.short_description = "Descripción"


@admin.register(ResultadoAprendizaje)
class ResultadoAprendizajeAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion_corta', 'competencia')
    list_filter = ('competencia__programa', 'competencia')
    search_fields = ('codigo', 'descripcion')

    def descripcion_corta(self, obj):
        return obj.descripcion[:60] + "..." if len(obj.descripcion) > 60 else obj.descripcion
    descripcion_corta.short_description = "Descripción del RAP"


class MatriculaInline(admin.TabularInline):
    model = Matricula
    extra = 1
    autocomplete_fields = ['aprendiz']


class HorarioFichaInline(admin.TabularInline):
    model = HorarioFicha
    extra = 1


@admin.register(Ficha)
class FichaAdmin(admin.ModelAdmin):
    list_display = ('codigo_ficha', 'programa', 'institucion', 'instructor_lider', 'estado', 'periodo_cerrado', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado', 'periodo_cerrado', 'institucion__municipio', 'institucion')
    search_fields = ('codigo_ficha', 'programa__denominacion', 'institucion__nombre', 'instructor_lider__first_name', 'instructor_lider__last_name')
    inlines = [MatriculaInline, HorarioFichaInline]


@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('aprendiz', 'ficha', 'grado_escolar', 'estado_formacion', 'fecha_matricula')
    list_filter = ('estado_formacion', 'grado_escolar', 'ficha__institucion')
    search_fields = ('aprendiz__first_name', 'aprendiz__last_name', 'aprendiz__username', 'ficha__codigo_ficha')


@admin.register(HorarioFicha)
class HorarioFichaAdmin(admin.ModelAdmin):
    list_display = ('ficha', 'dia', 'hora_inicio', 'hora_fin', 'instructor', 'modalidad', 'ambiente', 'activo')
    list_filter = ('dia', 'modalidad', 'activo', 'ficha__institucion')
    search_fields = ('ficha__codigo_ficha', 'instructor__first_name', 'instructor__last_name', 'tema', 'ambiente')
