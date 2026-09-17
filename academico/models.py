"""
Aplicación: academico
Modelos: ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula
Reglas de Negocio Asociadas: RN-002 (Pertenencia Escolar), RN-004 (Inmutabilidad Periodos), RN-007 (Grado 10/11)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from instituciones.models import InstitucionEducativa


class ProgramaFormacion(models.Model):
    """
    Programas de formación técnica curricular que imparte el Centro en articulación.
    Ejemplo: Técnico en Sistemas, Técnico en Asistencia Administrativa.
    """
    codigo_programa = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código del Programa (SOFIA)",
        help_text="Código oficial curricular nacional."
    )
    denominacion = models.CharField(
        max_length=200,
        verbose_name="Denominación del Programa"
    )
    version = models.CharField(
        max_length=10,
        default="1",
        verbose_name="Versión Curricular"
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="¿Programa Activo?"
    )

    class Meta:
        verbose_name = "Programa de Formación"
        verbose_name_plural = "Programas de Formación"
        ordering = ['denominacion']

    def __str__(self):
        return f"{self.denominacion} (Cód: {self.codigo_programa} - V.{self.version})"


class Competencia(models.Model):
    """
    Competencias laborales que integran el diseño curricular de un programa técnico.
    """
    programa = models.ForeignKey(
        ProgramaFormacion,
        on_delete=models.CASCADE,
        related_name='competencias',
        verbose_name="Programa de Formación"
    )
    codigo = models.CharField(
        max_length=20,
        verbose_name="Código de la Norma / Competencia"
    )
    descripcion = models.TextField(
        verbose_name="Descripción de la Competencia"
    )

    class Meta:
        verbose_name = "Competencia Laboral"
        verbose_name_plural = "Competencias Laborales"
        ordering = ['programa', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:80]}..."


class ResultadoAprendizaje(models.Model):
    """
    Resultados de Aprendizaje (RAP) que desglosan cada competencia y representan
    los logros que el instructor debe evaluar en SINETEC.
    """
    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.CASCADE,
        related_name='resultados',
        verbose_name="Competencia Asociada"
    )
    codigo = models.CharField(
        max_length=20,
        verbose_name="Código del RAP"
    )
    descripcion = models.TextField(
        verbose_name="Descripción del Resultado de Aprendizaje"
    )

    class Meta:
        verbose_name = "Resultado de Aprendizaje"
        verbose_name_plural = "Resultados de Aprendizaje"
        ordering = ['competencia', 'codigo']

    def __str__(self):
        return f"{self.codigo} - {self.descripcion[:80]}..."


class Ficha(models.Model):
    """
    Grupo o cohorte de aprendices de Media Técnica en un colegio bajo la guía de un instructor líder.
    """
    ESTADOS_FICHA = [
        ('En Ejecucion', 'En Ejecución'),
        ('Terminada', 'Terminada'),
        ('Cancelada', 'Cancelada'),
    ]

    codigo_ficha = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Ficha",
        help_text="Número identificador asignado al grupo en el Centro."
    )
    programa = models.ForeignKey(
        ProgramaFormacion,
        on_delete=models.PROTECT,
        related_name='fichas',
        verbose_name="Programa Técnico"
    )
    institucion = models.ForeignKey(
        InstitucionEducativa,
        on_delete=models.PROTECT,
        related_name='fichas',
        verbose_name="Institución Educativa Articulada"
    )
    instructor_lider = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='fichas_asignadas',
        verbose_name="Instructor Líder Responsable"
    )
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio Lectivo"
    )
    fecha_fin = models.DateField(
        verbose_name="Fecha Estimada de Finalización"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_FICHA,
        default='En Ejecucion',
        verbose_name="Estado de la Ficha"
    )
    # RN-004: Inmutabilidad de periodos cerrados formalmente
    periodo_cerrado = models.BooleanField(
        default=False,
        verbose_name="¿Periodo Evaluativo Cerrado Formalmente?",
        help_text="Si está marcado, se bloquea el registro y edición de calificaciones."
    )

    class Meta:
        verbose_name = "Ficha de Media Técnica"
        verbose_name_plural = "Fichas de Media Técnica"
        ordering = ['-fecha_inicio', 'codigo_ficha']

    def __str__(self):
        return f"Ficha {self.codigo_ficha} - {self.programa.denominacion} ({self.institucion.nombre})"


class Matricula(models.Model):
    """
    Vinculación formal del aprendiz a una Ficha de Media Técnica.
    """
    GRADOS_ESCOLARES = [
        ('10', 'Grado 10° (Décimo)'),
        ('11', 'Grado 11° (Undécimo)'),
    ]

    ESTADOS_APRENDIZ = [
        ('En Formacion', 'En Formación'),
        ('Desertado', 'Desertado'),
        ('Trasladado', 'Trasladado'),
        ('Retirado', 'Retiro Voluntario'),
        ('Certificado', 'Certificado'),
    ]

    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.CASCADE,
        related_name='matriculas',
        verbose_name="Ficha Asignada"
    )
    aprendiz = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='matriculas_academicas',
        verbose_name="Aprendiz"
    )
    fecha_matricula = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha de Matrícula"
    )
    # RN-007: Condición de grado escolar (10° u 11°)
    grado_escolar = models.CharField(
        max_length=5,
        choices=GRADOS_ESCOLARES,
        default='10',
        verbose_name="Grado Escolar en el Colegio"
    )
    estado_formacion = models.CharField(
        max_length=25,
        choices=ESTADOS_APRENDIZ,
        default='En Formacion',
        verbose_name="Estado de la Formación"
    )
    acudiente_nombre = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Nombre del Padre o Acudiente"
    )
    acudiente_telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono del Acudiente"
    )

    class Meta:
        verbose_name = "Matrícula de Aprendiz"
        verbose_name_plural = "Matrículas de Aprendices"
        # RN-002: Un aprendiz no puede matricularse dos veces en la misma ficha
        unique_together = ('ficha', 'aprendiz')
        ordering = ['ficha', 'aprendiz__last_name']

    def __str__(self):
        nombre_aprendiz = self.aprendiz.get_full_name() or self.aprendiz.username
        return f"{nombre_aprendiz} - {self.ficha.codigo_ficha} ({self.get_grado_escolar_display()})"


class HorarioFicha(models.Model):
    """Bloque editable del horario formativo de una ficha SENA."""
    DIAS = [(str(indice), nombre) for indice, nombre in enumerate(
        ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'), start=1
    )]
    MODALIDADES = [('Presencial', 'Presencial'), ('Virtual', 'Virtual'), ('Mixta', 'Mixta')]

    ficha = models.ForeignKey(Ficha, on_delete=models.CASCADE, related_name='horarios')
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='horarios_formativos')
    dia = models.CharField(max_length=1, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    ambiente = models.CharField(max_length=120, blank=True)
    modalidad = models.CharField(max_length=20, choices=MODALIDADES, default='Presencial')
    tema = models.CharField(max_length=180, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        return f'{self.ficha.codigo_ficha} · {self.get_dia_display()} {self.hora_inicio:%H:%M}'
