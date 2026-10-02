"""
Aplicación: academico
Modelos: ProgramaFormacion, Competencia, ResultadoAprendizaje, Ficha, Matricula, HorarioFicha
Reglas de Negocio Asociadas: RN-002 (Pertenencia Escolar), RN-004 (Inmutabilidad Periodos), RN-007 (Grado 10/11)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from instituciones.models import InstitucionEducativa


NIVELES_ESCOLARES = [
    ('Inicial', 'Inicial'),
    ('Primaria', 'Primaria'),
    ('Secundaria', 'Secundaria'),
]

GRADOS_POR_NIVEL = {
    'Inicial': ['3 años', '4 años', '5 años'],
    'Primaria': ['1er Grado', '2do Grado', '3er Grado', '4to Grado', '5to Grado'],
    'Secundaria': ['6to Grado', '7mo Grado', '8vo Grado', '9no Grado', '10mo Grado', '11mo Grado'],
}

SECCIONES_ESCOLARES = ['A', 'B', 'C']


def formato_hora_ampm(hora):
    if not hora:
        return ''
    hora_12 = hora.hour % 12 or 12
    sufijo = 'AM' if hora.hour < 12 else 'PM'
    return f'{hora_12:02d}:{hora.minute:02d} {sufijo}'


class ProgramaFormacion(models.Model):
    """
    Programas de formación técnica curricular que imparte el Centro en articulación.
    Ejemplo: Técnico en Sistemas, Técnico en Asistencia Administrativa.
    """
    TIPO_CHOICES = [
        ('Técnico', 'Técnico Laboral / Media Técnica'),
        ('Tecnólogo', 'Tecnólogo'),
        ('Curso Especial', 'Curso Especial'),
        ('Formación Complementaria', 'Formación Complementaria'),
        ('Otro', 'Otro Programa'),
    ]

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
    tipo_programa = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        default='Técnico',
        verbose_name="Tipo de Formación"
    )
    duracion_meses = models.PositiveIntegerField(
        default=12,
        verbose_name="Duración Estimada (Meses)"
    )
    duracion_horas = models.PositiveIntegerField(
        default=880,
        verbose_name="Intensidad Horaria Total (Horas)"
    )
    institucion = models.ForeignKey(
        'instituciones.InstitucionEducativa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programas_articulados',
        verbose_name="Colegio / Institución Sede"
    )
    convenio = models.ForeignKey(
        'convenios.ConvenioSENA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='programas_asociados',
        verbose_name="Convenio SENA Vinculado"
    )
    responsable = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Responsable / Instructor Líder"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones Curriculares"
    )
    fecha_inicio = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Inicio"
    )
    fecha_fin = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Finalización"
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

class Objetivo(models.Model):
    """
    Objetivos específicos que se desprenden de una competencia.
    """
    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.CASCADE,
        related_name='objetivos',
        verbose_name="Competencia Asociada"
    )
    descripcion = models.TextField(
        verbose_name="Descripción del Objetivo"
    )

    class Meta:
        verbose_name = "Objetivo"
        verbose_name_plural = "Objetivos"

    def __str__(self):
        return f"Objetivo: {self.descripcion[:80]}..."


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
    Grupo o cohorte de estudiantes de Media Técnica en un colegio bajo la guía de un profesor líder.
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
        verbose_name="Profesor Líder Responsable"
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
        ('1', '1° Grado (Primaria)'),
        ('2', '2° Grado (Primaria)'),
        ('3', '3° Grado (Primaria)'),
        ('4', '4° Grado (Primaria)'),
        ('5', '5° Grado (Primaria)'),
        ('6', '6° Grado (Secundaria)'),
        ('7', '7° Grado (Secundaria)'),
        ('8', '8° Grado (Secundaria)'),
        ('9', '9° Grado (Secundaria)'),
        ('10', '10° Grado (Bachillerato)'),
        ('11', '11° Grado (Bachillerato)'),
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
        verbose_name="Estudiante"
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
    seccion = models.CharField(max_length=4, default='A', verbose_name="Sección Escolar")
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
    """Bloque editable del horario escolar por nivel, grado, sección y día."""
    DIAS = [(str(indice), nombre) for indice, nombre in enumerate(
        ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'), start=1
    )]
    MODALIDADES = [('Presencial', 'Presencial'), ('Virtual', 'Virtual'), ('Mixta', 'Mixta')]

    ficha = models.ForeignKey(
        Ficha, on_delete=models.SET_NULL, related_name='horarios',
        null=True, blank=True
    )
    instructor = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='horarios_formativos',
        null=True, blank=True
    )
    programa = models.ForeignKey(
        ProgramaFormacion, on_delete=models.SET_NULL, related_name='horarios',
        null=True, blank=True, verbose_name="Materia / Curso"
    )
    dia = models.CharField(max_length=1, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    ambiente = models.CharField(max_length=120, blank=True)
    modalidad = models.CharField(max_length=20, choices=MODALIDADES, default='Presencial')
    tema = models.CharField(max_length=180, blank=True)
    nivel = models.CharField(max_length=20, choices=NIVELES_ESCOLARES, blank=True, default='')
    grado = models.CharField(max_length=40, blank=True, default='')
    seccion = models.CharField(max_length=4, blank=True, default='A')
    es_recreo = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    color_hex = models.CharField(max_length=7, blank=True, default='#E2E8F0', verbose_name="Color del Bloque")

    class Meta:
        verbose_name = "Horario de Ficha"
        verbose_name_plural = "Horarios de Fichas"
        ordering = ['dia', 'hora_inicio']

    def __str__(self):
        materia = self.nombre_materia
        return f'{materia} · {self.get_dia_display()} {self.hora_inicio:%H:%M}'

    @property
    def nombre_materia(self):
        if self.es_recreo:
            return 'RECREO / ALMUERZO'
        if self.tema:
            return self.tema
        if self.programa:
            return self.programa.denominacion
        if self.ficha and self.ficha.programa:
            return self.ficha.programa.denominacion
        return 'Clase'

    @property
    def hora_inicio_ampm(self):
        return formato_hora_ampm(self.hora_inicio)

    @property
    def hora_fin_ampm(self):
        return formato_hora_ampm(self.hora_fin)

    def clean(self):
        super().clean()
        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError({
                'hora_fin': "La hora final debe ser posterior a la hora inicial del bloque formativo."
            })


class CargaAcademica(models.Model):
    """Asignación de un docente a una materia, grado y sección."""
    profesor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cargas_academicas'
    )
    programa = models.ForeignKey(
        ProgramaFormacion, on_delete=models.CASCADE, related_name='cargas_academicas'
    )
    nivel = models.CharField(max_length=20, choices=NIVELES_ESCOLARES)
    grado = models.CharField(max_length=40)
    seccion = models.CharField(max_length=4, default='A')
    anio_lectivo = models.PositiveIntegerField(default=2026)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Carga Académica"
        verbose_name_plural = "Cargas Académicas"
        ordering = ['nivel', 'grado', 'programa__denominacion']
        unique_together = ('profesor', 'programa', 'nivel', 'grado', 'seccion', 'anio_lectivo')

    def __str__(self):
        nombre = self.profesor.get_full_name() or self.profesor.username
        return f'{self.programa.denominacion} · {nombre} · {self.grado} {self.seccion}'


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


class SemaforoCompetencia(models.Model):
    """
    Semáforo de Competencias y Logros para el seguimiento formativo del estudiante.
    Permite al profesor calificar y monitorear visualmente con 3 estados:
    🟢 Aprobado (APROBADO)
    🟡 En proceso (EN_PROCESO)
    🔴 Por recuperar (RECUPERAR)
    """
    ESTADOS = [
        ('APROBADO', 'Aprobado'),         # 🟢 Verde
        ('EN_PROCESO', 'En proceso'),     # 🟡 Amarillo
        ('RECUPERAR', 'Por recuperar'),   # 🔴 Rojo
    ]

    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='semaforo_competencias',
        verbose_name="Estudiante Matriculado"
    )
    competencia = models.ForeignKey(
        Competencia,
        on_delete=models.CASCADE,
        related_name='evaluaciones_semaforo',
        verbose_name="Competencia Laboral"
    )
    resultado_aprendizaje = models.ForeignKey(
        ResultadoAprendizaje,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='evaluaciones_semaforo',
        verbose_name="Resultado de Aprendizaje (RAP)"
    )
    profesor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='calificaciones_semaforo',
        verbose_name="Profesor / Evaluador"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='EN_PROCESO',
        verbose_name="Estado del Semáforo"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones Pedagógicas / Plan de Mejora"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Asignación"
    )

    class Meta:
        verbose_name = "Semáforo de Competencia"
        verbose_name_plural = "Semáforo de Competencias"
        unique_together = ('matricula', 'competencia', 'resultado_aprendizaje')
        ordering = ['matricula', 'competencia', 'resultado_aprendizaje']

    def __str__(self):
        rap_str = f" - RAP {self.resultado_aprendizaje.codigo}" if self.resultado_aprendizaje else ""
        return f"{self.matricula.aprendiz.get_full_name()} · {self.competencia.codigo}{rap_str}: [{self.get_estado_display()}]"

    @property
    def color_badge(self):
        if self.estado == 'APROBADO':
            return 'bg-success text-white'
        elif self.estado == 'EN_PROCESO':
            return 'bg-warning text-dark'
        elif self.estado == 'RECUPERAR':
            return 'bg-danger text-white'
        return 'bg-secondary text-white'

    @property
    def color_icono(self):
        if self.estado == 'APROBADO':
            return '🟢'
        elif self.estado == 'EN_PROCESO':
            return '🟡'
        elif self.estado == 'RECUPERAR':
            return '🔴'
        return '⚪'

class MaterialClase(models.Model):
    carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, related_name='materiales')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='materiales_clase/%Y/%m/', blank=True, null=True)
    enlace = models.URLField(blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Material de Clase"
        verbose_name_plural = "Materiales de Clase"

class TareaClase(models.Model):
    carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, related_name='tareas')
    tipo_actividad = models.CharField(max_length=50, default='Tarea', verbose_name="Tipo de Actividad")
    competencia = models.ForeignKey('Competencia', on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_clase', verbose_name="Competencia Evaluada")
    objetivo = models.ForeignKey('Objetivo', on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_clase', verbose_name="Objetivo Evaluado")
    resultado_aprendizaje = models.ForeignKey('ResultadoAprendizaje', on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_clase', verbose_name="Resultado de Aprendizaje")
    criterio_evaluacion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Criterio de Evaluación")
    titulo = models.CharField(max_length=200)
    instrucciones = models.TextField()
    archivo = models.FileField(upload_to='tareas_clase/%Y/%m/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(blank=True, null=True)
    puntaje_maximo = models.DecimalField(max_digits=4, decimal_places=2, default=5.0)
    estado = models.CharField(max_length=20, default='Publicada', choices=[
        ('Borrador', 'Borrador'),
        ('Publicada', 'Publicada'),
        ('Cerrada', 'Cerrada')
    ], verbose_name="Estado de la Actividad")
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=20.0, verbose_name="Porcentaje")
    es_calificada = models.BooleanField(default=True, verbose_name="¿Es Calificada?")
    enlace_externo = models.URLField(max_length=500, blank=True, null=True, verbose_name="Enlace de Apoyo")
    periodo = models.CharField(max_length=50, default='Periodo 1', verbose_name="Periodo Académico")

    class Meta:
        verbose_name = "Tarea de Clase"
        verbose_name_plural = "Tareas de Clase"


class EntregaTarea(models.Model):
    ESTADOS_ENTREGA = [
        ('PENDIENTE', 'Pendiente'),
        ('ENTREGADA', 'Entregada'),
        ('ENTREGADA_TARDE', 'Entregada fuera de plazo'),
        ('CALIFICADA', 'Calificada'),
        ('DEVUELTA', 'Devuelta'),
    ]
    tarea = models.ForeignKey(TareaClase, on_delete=models.CASCADE, related_name='entregas')
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tareas_entregadas')
    respuesta = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='entregas_tareas/%Y/%m/', blank=True, null=True)
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    calificacion = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    retroalimentacion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_ENTREGA, default='PENDIENTE')

    class Meta:
        verbose_name = "Entrega de Tarea"
        verbose_name_plural = "Entregas de Tareas"
        unique_together = ('tarea', 'estudiante')

class GuiaClase(models.Model):
    carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, related_name='guias')
    titulo = models.CharField(max_length=200)
    instrucciones = models.TextField()
    archivo = models.FileField(upload_to='guias_clase/%Y/%m/', blank=True, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Guía de Clase"
        verbose_name_plural = "Guías de Clase"

class ActividadClase(models.Model):
    carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, related_name='actividades')
    titulo = models.CharField(max_length=200)
    instrucciones = models.TextField()
    archivo = models.FileField(upload_to='actividades_clase/%Y/%m/', blank=True, null=True)
    fecha_actividad = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Actividad de Clase"
        verbose_name_plural = "Actividades de Clase"

class AvisoClase(models.Model):
    carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, related_name='avisos')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Aviso de Clase"
        verbose_name_plural = "Avisos de Clase"


class CalificacionEscolar(models.Model):
    """
    Registro oficial de calificaciones escolares por periodo y materia del docente.
    """
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE, related_name='calificaciones_escolares')
    profesor = models.ForeignKey(User, on_delete=models.PROTECT, related_name='calificaciones_docente')
    carga_academica = models.ForeignKey(CargaAcademica, on_delete=models.CASCADE, null=True, blank=True, related_name='calificaciones_escolares')
    periodo = models.CharField(max_length=50, default='Periodo 1')
    nota = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    desempeno = models.CharField(max_length=20, default='Básico')
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Calificación Escolar"
        verbose_name_plural = "Calificaciones Escolares"
        ordering = ['-fecha_registro']
        constraints = [
            models.UniqueConstraint(fields=['matricula', 'carga_academica', 'periodo'], name='calificacion_escolar_unica_periodo')
        ]

    def save(self, *args, **kwargs):
        if self.nota is not None:
            try:
                n = float(self.nota)
                if n >= 4.6:
                    self.desempeno = 'Superior'
                elif n >= 4.0:
                    self.desempeno = 'Alto'
                elif n >= 3.0:
                    self.desempeno = 'Básico'
                else:
                    self.desempeno = 'Bajo'
            except (ValueError, TypeError):
                self.desempeno = 'Básico'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.matricula} - {self.periodo}: {self.nota}"

class ComunicacionMensaje(models.Model):
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comunicaciones_enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='comunicaciones_recibidas')
    grupo_destino = models.CharField(max_length=50, blank=True, null=True) # '10', '11', etc.
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    archivo = models.FileField(upload_to='comunicaciones/%Y/%m/', blank=True, null=True)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    eliminado_por_remitente = models.BooleanField(default=False)
    eliminado_por_destinatario = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Comunicación"
        verbose_name_plural = "Comunicaciones"
        ordering = ['-fecha_envio']
