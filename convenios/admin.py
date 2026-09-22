from django.contrib import admin
from .models import InstitucionConvenio, ConvenioSENA, DocumentoConvenio


class DocumentoConvenioInline(admin.TabularInline):
    model = DocumentoConvenio
    extra = 1


class ConvenioSENAInline(admin.StackedInline):
    model = ConvenioSENA
    extra = 1


@admin.register(InstitucionConvenio)
class InstitucionConvenioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'municipio', 'departamento', 'codigo_dane', 'telefono', 'activo', 'fecha_registro']
    list_filter = ['activo', 'departamento', 'municipio']
    search_fields = ['nombre', 'municipio', 'codigo_dane']
    inlines = [ConvenioSENAInline]


@admin.register(ConvenioSENA)
class ConvenioSENAAdmin(admin.ModelAdmin):
    list_display = ['numero_convenio', 'nombre', 'institucion', 'tipo_convenio', 'fecha_inicio', 'fecha_fin', 'estado_actual']
    list_filter = ['tipo_convenio', 'estado_manual']
    search_fields = ['numero_convenio', 'nombre', 'institucion__nombre']
    inlines = [DocumentoConvenioInline]

    def estado_actual(self, obj):
        return obj.estado
    estado_actual.short_description = "Estado Dinámico"


@admin.register(DocumentoConvenio)
class DocumentoConvenioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'convenio', 'tipo', 'fecha_carga', 'usuario_carga']
    list_filter = ['tipo', 'fecha_carga']
    search_fields = ['nombre', 'convenio__numero_convenio', 'convenio__institucion__nombre']
