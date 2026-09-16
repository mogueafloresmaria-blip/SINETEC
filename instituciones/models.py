"""
Aplicación: instituciones
Modelo: InstitucionEducativa
Reglas de Negocio: Código DANE único, directorio de colegios articulados en el Magdalena
"""

from django.db import models


class InstitucionEducativa(models.Model):
    """
    Representa una Institución Educativa (colegio) del Departamento del Magdalena
    que mantiene convenio de articulación con el Centro de Logística y Promoción Ecoturística.
    """
    codigo_dane = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código DANE Oficial",
        help_text="Código único asignado por el DANE / MEN al colegio."
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre Oficial de la Institución Educativa"
    )
    municipio = models.CharField(
        max_length=100,
        verbose_name="Municipio del Magdalena",
        help_text="Municipio donde está ubicada la sede principal."
    )
    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Dirección Física"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono Institucional"
    )
    rector_nombre = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nombre del Rector(a)"
    )
    rector_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo del Rector(a)"
    )
    enlace_nombre = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nombre del Docente Enlace / Coordinador"
    )
    enlace_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono del Docente Enlace"
    )
    enlace_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo del Docente Enlace"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="¿Convenio Activo y Vigente?"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro en SINETEC"
    )

    class Meta:
        verbose_name = "Institución Educativa"
        verbose_name_plural = "Instituciones Educativas"
        ordering = ['municipio', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.municipio} - DANE: {self.codigo_dane})"

    # --- NUBES Y MÉTODOS DE CONTEO PARA LA COLUMNA FICHAS / ALUMNOS ---

    def total_fichas(self):
        """ Retorna el total de fichas asociadas a esta institución """
        if hasattr(self, 'fichas'):
            return self.fichas.count()
        return 0

    def total_estudiantes(self):
        """ Retorna el total de estudiantes/aprendices asociados a las fichas de esta institución """
        if hasattr(self, 'fichas'):
            total = 0
            for ficha in self.fichas.all():
                if hasattr(ficha, 'estudiantes'):
                    total += ficha.estudiantes.count()
                elif hasattr(ficha, 'aprendices'):
                    total += ficha.aprendices.count()
            return total
        return 0