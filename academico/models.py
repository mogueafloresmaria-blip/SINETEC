"""
Aplicación: academico
Modelos: ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula, HorarioFicha
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

    def clean(self):
        super().clean()
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin <= self.fecha_inicio:
            raise ValidationError({
                'fecha_fin': "La fecha estimada de finalización debe ser posterior a la fecha de inicio lectivo."
            })


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
        ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'), start=1
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
        verbose_name = "Horario de Ficha"
        verbose_name_plural = "Horarios de Fichas"
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        return f'{self.ficha.codigo_ficha} · {self.get_dia_display()} {self.hora_inicio:%H:%M}'

    def clean(self):
        super().clean()
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError({
                'hora_fin': "La hora final debe ser posterior a la hora inicial del bloque formativo."
            })


class RecursoBiblioteca(models.Model):
    """
    Catálogo bibliográfico oficial SENA: Libros, Guías de Aprendizaje,
    Manuales Técnicos, Diseños Curriculares SOFIA y Documentos Técnicos.
    """
    CATEGORIAS = [
        ('Libro Tecnico', 'Libro Técnico'),
        ('Manual SENA', 'Manual SENA'),
        ('Guia de Aprendizaje', 'Guía de Aprendizaje'),
        ('Diseno Curricular', 'Diseño Curricular SOFIA'),
        ('Documento Tecnico', 'Documento Técnico / Estándar'),
        ('Publicacion', 'Publicación Académica'),
    ]

    titulo = models.CharField(max_length=220, verbose_name="Título del Recurso")
    autor = models.CharField(max_length=160, default="SENA Regional Magdalena", verbose_name="Autor / Entidad")
    categoria = models.CharField(max_length=40, choices=CATEGORIAS, default='Guia de Aprendizaje')
    tipo_recurso = models.CharField(max_length=60, default="Documento Digital PDF")
    descripcion = models.TextField(verbose_name="Descripción y Contenido")
    programa = models.ForeignKey(ProgramaFormacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='recursos_biblioteca')
    ano_publicacion = models.IntegerField(default=2026, verbose_name="Año de Publicación")
    archivo_adjunto = models.FileField(upload_to='biblioteca_recursos/%Y/', blank=True, null=True)
    url_externa = models.URLField(blank=True, null=True, verbose_name="Enlace de Consulta Externa")
    disponible = models.BooleanField(default=True, verbose_name="Disponible para Descarga")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Recurso de Biblioteca"
        verbose_name_plural = "Recursos de Biblioteca"
        ordering = ['-ano_publicacion', 'titulo']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo}"


class RecursoGuardadoAprendiz(models.Model):
    """
    Recursos guardados / favoritos por el aprendiz en su espacio 'Mis Recursos'.
    """
    aprendiz = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recursos_guardados')
    recurso = models.ForeignKey(RecursoBiblioteca, on_delete=models.CASCADE, related_name='guardados_por')
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('aprendiz', 'recurso')
        verbose_name = "Recurso Guardado por Aprendiz"
        verbose_name_plural = "Recursos Guardados por Aprendices"
        ordering = ['-fecha_guardado']

    def __str__(self):
        return f"{self.aprendiz.username} guardó {self.recurso.titulo}"


class ProyectoInnovacion(models.Model):
    """
    Centro de Innovación y Emprendimiento SENA (Ideas, Proyectos, Prototipos y Emprendimientos).
    """
    ESTADOS = [
        ('IDEA', 'Idea en Conceptualización'),
        ('PROPUESTA', 'Propuesta Radicada'),
        ('EN_EVALUACION', 'En Evaluación de Comité'),
        ('EN_DESARROLLO', 'En Desarrollo Activo'),
        ('FINALIZADO', 'Proyecto Finalizado / Transferido'),
    ]

    CATEGORIAS = [
        ('Software TIC', 'Desarrollo de Software y TIC'),
        ('Agroecologia', 'Agroecología y Biotecnología'),
        ('Ecoturismo', 'Ecoturismo y Hotelería Regional'),
        ('Logistica', 'Logística y Comercio Portuario'),
        ('Emprendimiento', 'Emprendimiento Comunitario'),
    ]

    titulo = models.CharField(max_length=220, verbose_name="Título del Proyecto / Idea")
    descripcion = models.TextField(verbose_name="Descripción, Justificación e Impacto")
    lider = models.ForeignKey(User, on_delete=models.PROTECT, related_name='proyectos_innovacion_liderados', verbose_name="Aprendiz / Instructor Líder")
    ficha = models.ForeignKey(Ficha, on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos_innovacion', verbose_name="Ficha Formativa")
    instructor_asesor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos_innovacion_asesorados', verbose_name="Instructor Asesor Técnico")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Software TIC', verbose_name="Línea Tecnológica")
    estado = models.CharField(max_length=30, choices=ESTADOS, default='IDEA', verbose_name="Estado de Madurez")
    archivo_soporte = models.FileField(upload_to='proyectos_innovacion/%Y/%m/', blank=True, null=True, verbose_name="Ficha Técnica o Documento de Propuesta")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Proyecto de Innovación"
        verbose_name_plural = "Proyectos de Innovación"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.get_estado_display()}] {self.titulo}"


class LogroAprendiz(models.Model):
    """
    Sistema de Gamificación Formativa: Insignias y reconocimientos de excelencia (asistencia, cumplimiento, liderazgo).
    """
    aprendiz = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logros_obtenidos', verbose_name="Aprendiz Destacado")
    titulo = models.CharField(max_length=120, verbose_name="Nombre de la Insignia")
    descripcion = models.CharField(max_length=255, verbose_name="Mérito Reconocido")
    icono = models.CharField(max_length=60, default='bi-trophy-fill', verbose_name="Icono Bootstrap")
    color = models.CharField(max_length=30, default='success', verbose_name="Color de la Insignia")
    categoria = models.CharField(max_length=50, default='Puntualidad y Asistencia', verbose_name="Categoría")
    fecha_otorgado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Logro / Insignia Formativa"
        verbose_name_plural = "Logros e Insignias Formativas"
        ordering = ['-fecha_otorgado']

    def __str__(self):
        return f"{self.aprendiz.get_full_name()} · {self.titulo}"


class DocumentoInstitucional(models.Model):
    """
    Gestión Documental oficial SENA con clasificación, control de versiones y permisos RBAC.
    """
    CATEGORIAS = [
        ('Formato Oficial SENA', 'Formato Oficial SENA (PE-04 / F023)'),
        ('Guia Pedagogica', 'Guía de Aprendizaje Pedagógica'),
        ('Acta de Comite', 'Acta de Comité de Evaluación'),
        ('Paz y Salvo', 'Paz y Salvo y Certificaciones'),
        ('Normativa Institucional', 'Normativa y Circulares del Centro'),
    ]

    titulo = models.CharField(max_length=220, verbose_name="Título del Documento")
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='Formato Oficial SENA', verbose_name="Categoría")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Contenido")
    archivo = models.FileField(upload_to='gestion_documental/%Y/%m/', verbose_name="Archivo Digital (PDF / Word / Excel)")
    version = models.CharField(max_length=10, default='1.0', verbose_name="Versión")
    subido_por = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Funcionario que Publica")
    roles_permitidos = models.CharField(
        max_length=255,
        default='Todos',
        verbose_name="Roles Autorizados",
        help_text="Escribir 'Todos' o roles separados por coma: Ej: Coordinador,Instructor SENA,Secretaría"
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Documento Institucional"
        verbose_name_plural = "Documentos Institucionales"
        ordering = ['-fecha_subida']

    def __str__(self):
        return f"[{self.version}] {self.titulo} ({self.get_categoria_display()})"

