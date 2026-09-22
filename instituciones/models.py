"""
Aplicación: instituciones
Modelo: InstitucionEducativa
Reglas de Negocio: Código DANE único, directorio de colegios articulados en el Magdalena
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
    correo = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo Electrónico Institucional"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observaciones Generales"
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
                if hasattr(ficha, 'matriculas'):
                    total += ficha.matriculas.count()
                elif hasattr(ficha, 'estudiantes'):
                    total += ficha.estudiantes.count()
                elif hasattr(ficha, 'aprendices'):
                    total += ficha.aprendices.count()
            return total
        return 0

    @property
    def total_contactos(self):
        return self.contactos.count() if hasattr(self, 'contactos') else 0

    @property
    def total_convenios(self):
        if hasattr(self, 'convenios_sena'):
            return self.convenios_sena.count()
        return 0


class ContactoInstitucional(models.Model):
    """
    Directorio de contactos clave dentro de las Instituciones Educativas (Colegios).
    Permite almacenar rectores, coordinadores, encargados y enlaces con comunicación directa.
    """
    TIPO_CHOICES = [
        ('Rector', 'Rector(a)'),
        ('Coordinador', 'Coordinador(a) Académico'),
        ('Encargado Convenio', 'Encargado(a) del Convenio SENA'),
        ('Docente Enlace', 'Docente Enlace de Media Técnica'),
        ('Administrativo', 'Personal Administrativo'),
        ('Secretaria', 'Secretaría del Colegio'),
        ('Orientador', 'Orientador(a) Escolar'),
        ('Otro', 'Otro Contacto Institucional'),
    ]

    ESTADO_CHOICES = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    ]

    institucion = models.ForeignKey(
        InstitucionEducativa,
        on_delete=models.CASCADE,
        related_name='contactos',
        verbose_name="Colegio / Institución"
    )
    nombre = models.CharField(max_length=120, verbose_name="Nombre(s)")
    apellido = models.CharField(max_length=120, verbose_name="Apellido(s)")
    cargo = models.CharField(max_length=120, verbose_name="Cargo o Función")
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono / Celular")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='Coordinador', verbose_name="Tipo de Contacto")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Activo', verbose_name="Estado")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones / Horario de Atención")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Contacto Institucional"
        verbose_name_plural = "Contactos Institucionales"
        ordering = ['institucion', 'apellido', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cargo} ({self.institucion.nombre})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()


class ObservacionInstitucional(models.Model):
    """
    Registro y trazabilidad de reuniones, acuerdos, novedades, antecedentes, compromisos,
    incidencias y visitas de articulación para cada Institución Educativa.
    """
    TIPO_CHOICES = [
        ('Reunión', 'Reunión Institucional'),
        ('Seguimiento', 'Seguimiento Administrativo'),
        ('Acuerdo', 'Acuerdo / Compromiso'),
        ('Novedad', 'Novedad Institucional'),
        ('Antecedente', 'Antecedente Histórico'),
        ('Compromiso', 'Compromiso Formal'),
        ('Incidencia', 'Incidencia / Problema Reportado'),
        ('Visita', 'Visita Técnica / Protocolaria'),
        ('Otro', 'Otro Registro'),
    ]

    PRIORIDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Atendido', 'Atendido / Cumplido'),
        ('Cerrado', 'Cerrado'),
    ]

    institucion = models.ForeignKey(
        InstitucionEducativa,
        on_delete=models.CASCADE,
        related_name='observaciones_admin',
        verbose_name="Colegio / Institución"
    )
    convenio = models.ForeignKey(
        'convenios.ConvenioSENA',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='observaciones_institucionales',
        verbose_name="Convenio Asociado (Opcional)"
    )
    fecha = models.DateField(default=timezone.localdate, verbose_name="Fecha del Registro")
    titulo = models.CharField(max_length=200, verbose_name="Título del Asunto")
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES, default='Reunión', verbose_name="Tipo de Observación")
    descripcion = models.TextField(verbose_name="Descripción Detallada")
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='observaciones_registradas',
        verbose_name="Funcionario Responsable"
    )
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='Media', verbose_name="Prioridad")
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='Pendiente', verbose_name="Estado de Atención")
    fecha_seguimiento = models.DateField(blank=True, null=True, verbose_name="Fecha Límite / Próximo Seguimiento")
    resultado = models.TextField(blank=True, null=True, verbose_name="Resultado / Conclusiones")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Observación / Antecedente Institucional"
        verbose_name_plural = "Observaciones y Antecedentes"
        ordering = ['-fecha', '-fecha_registro']

    def __str__(self):
        return f"[{self.tipo}] {self.titulo} - {self.institucion.nombre}"