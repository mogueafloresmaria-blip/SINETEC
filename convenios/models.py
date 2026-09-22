from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class InstitucionConvenio(models.Model):
    """
    Catálogo administrativo de Instituciones Educativas articuladas o con convenios SENA.
    Módulo 100% independiente de la gestión académica operativa.
    """
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Institución")
    codigo_dane = models.CharField(max_length=30, blank=True, null=True, verbose_name="Código DANE")
    departamento = models.CharField(max_length=100, default='Magdalena', verbose_name="Departamento")
    municipio = models.CharField(max_length=100, verbose_name="Municipio")
    direccion = models.CharField(max_length=255, verbose_name="Dirección")
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono")
    correo = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    sitio_web = models.URLField(blank=True, null=True, verbose_name="Sitio Web")
    
    nombre_contacto = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre del Contacto")
    cargo_contacto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Cargo del Contacto")
    telefono_contacto = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono del Contacto")
    correo_contacto = models.EmailField(blank=True, null=True, verbose_name="Correo del Contacto")
    
    activo = models.BooleanField(default=True, verbose_name="¿Institución Activa?")
    logo = models.ImageField(upload_to='convenios/logos/%Y/%m/', blank=True, null=True, verbose_name="Logo Institucional")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción de la Institución")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Institución de Convenio"
        verbose_name_plural = "Instituciones de Convenios"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.municipio})"

    @property
    def convenio_activo(self):
        """Retorna el convenio vigente más relevante de la institución."""
        for conv in self.convenios.all():
            if conv.estado in ['Activo', 'Próximo a vencer']:
                return conv
        return self.convenios.first()

    @property
    def estado_convenio_resumen(self):
        conv = self.convenio_activo
        if conv:
            return conv.estado
        return "Sin Convenio"

    @property
    def estado_badge_class(self):
        conv = self.convenio_activo
        if conv:
            return conv.estado_badge_class
        return "bg-secondary text-white"


class ConvenioSENA(models.Model):
    """
    Convenio administrativo formal suscrito entre el SENA y una Institución Educativa.
    """
    TIPO_CHOICES = [
        ('Articulacion Media Tecnica', 'Articulación Media Técnica'),
        ('Pasantias y Practicas', 'Pasantías y Prácticas'),
        ('Marco de Cooperacion', 'Marco de Cooperación'),
        ('Especifico', 'Convenio Específico'),
        ('Comodato', 'Comodato de Equipos e Infraestructura'),
        ('Otro', 'Otro Convenio'),
    ]

    ESTADO_MANUAL_CHOICES = [
        ('Suspendido', 'Suspendido'),
        ('Finalizado', 'Finalizado'),
    ]

    institucion = models.ForeignKey(
        InstitucionConvenio,
        on_delete=models.CASCADE,
        related_name='convenios',
        verbose_name="Institución Educativa"
    )
    institucion_educativa = models.ForeignKey(
        'instituciones.InstitucionEducativa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='convenios_sena',
        verbose_name="Institución Educativa Articulada"
    )
    numero_convenio = models.CharField(max_length=50, unique=True, verbose_name="Número o Código del Convenio")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Convenio")
    tipo_convenio = models.CharField(max_length=80, choices=TIPO_CHOICES, default='Articulacion Media Tecnica', verbose_name="Tipo de Convenio")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del Convenio")
    objetivo = models.TextField(blank=True, null=True, verbose_name="Objetivo del Convenio")
    fecha_inicio = models.DateField(verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(verbose_name="Fecha de Finalización")
    responsable = models.CharField(max_length=150, verbose_name="Responsable SENA / Institucional")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")
    estado_manual = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=ESTADO_MANUAL_CHOICES,
        verbose_name="Estado Forzado / Manual (Opcional)"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = "Convenio SENA"
        verbose_name_plural = "Convenios SENA"
        ordering = ['-fecha_fin', 'nombre']

    def __str__(self):
        nombre_inst = self.institucion_educativa.nombre if self.institucion_educativa else (self.institucion.nombre if self.institucion else "Sin I.E.")
        return f"{self.numero_convenio} - {self.nombre} ({nombre_inst})"

    @property
    def colegio(self):
        """Retorna la InstitucionEducativa asociada o InstitucionConvenio."""
        if self.institucion_educativa:
            return self.institucion_educativa
        return self.institucion

    @property
    def total_beneficios(self):
        return self.beneficios.count() if hasattr(self, 'beneficios') else 0

    @property
    def dias_para_vencer(self):
        hoy = timezone.localdate()
        if self.fecha_fin:
            return (self.fecha_fin - hoy).days
        return None

    @property
    def alerta_vencimiento(self):
        dias = self.dias_para_vencer
        if dias is not None:
            if dias < 0:
                return f"Convenio vencido hace {abs(dias)} días."
            elif dias == 0:
                return "Este convenio vence HOY."
            elif dias <= 30:
                return f"¡Atención! Este convenio vence en {dias} días."
        return None

    @property
    def estado(self):
        """
        Cálculo dinámico y automático del estado del convenio.
        Nunca se ingresa manualmente por el usuario (salvo suspensión/finalización voluntaria).
        """
        if self.estado_manual:
            return self.estado_manual

        if not self.fecha_inicio or not self.fecha_fin:
            return "Activo"

        hoy = timezone.localdate()
        if self.fecha_fin < hoy:
            return "Vencido"
        elif self.fecha_fin <= hoy + timedelta(days=30):
            return "Próximo a vencer"
        elif self.fecha_inicio > hoy:
            return "Próximo a iniciar"
        else:
            return "Activo"

    @property
    def estado_calculado(self):
        return self.estado

    @property
    def estado_badge_class(self):
        st = self.estado
        if st == 'Activo':
            return 'bg-success text-white'
        elif st == 'Próximo a vencer':
            return 'bg-warning text-dark'
        elif st == 'Vencido':
            return 'bg-danger text-white'
        elif st == 'Suspendido':
            return 'bg-secondary text-white'
        elif st == 'Finalizado':
            return 'bg-dark text-white'
        return 'bg-info text-white'


class BeneficioConvenio(models.Model):
    """
    Beneficios específicos otorgados o gestionados bajo el marco de un Convenio SENA
    (ej: cursos cortos, certificaciones técnicas, acceso a programas,
    formación complementaria, talleres de orientación, dotación).
    """
    TIPO_BENEFICIO_CHOICES = [
        ('Cursos', 'Cursos de Formación'),
        ('Certificaciones', 'Certificaciones Técnicas'),
        ('Acceso a Programas', 'Acceso Preferencial a Programas'),
        ('Formación Complementaria', 'Formación Complementaria Especial'),
        ('Actividades', 'Actividades / Talleres de Innovación'),
        ('Orientación', 'Orientación Ocupacional y Empleo'),
        ('Beneficios Especiales', 'Beneficios Especiales / Dotación'),
        ('Otro', 'Otro Beneficio'),
    ]

    ESTADO_CHOICES = [
        ('Activo', 'Activo / Disponible'),
        ('En Ejecución', 'En Ejecución'),
        ('Cumplido', 'Cumplido / Culminado'),
        ('Cancelado', 'Cancelado'),
    ]

    convenio = models.ForeignKey(
        ConvenioSENA,
        on_delete=models.CASCADE,
        related_name='beneficios',
        verbose_name="Convenio SENA"
    )
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Beneficio")
    tipo = models.CharField(max_length=60, choices=TIPO_BENEFICIO_CHOICES, default='Cursos', verbose_name="Tipo de Beneficio")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción y Alcance")
    cantidad_cupos = models.PositiveIntegerField(default=30, verbose_name="Cupos Estimados / Población Beneficiaria")
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='Activo', verbose_name="Estado")
    fecha_inicio = models.DateField(blank=True, null=True, verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(blank=True, null=True, verbose_name="Fecha de Finalización")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    class Meta:
        verbose_name = "Beneficio de Convenio"
        verbose_name_plural = "Beneficios de Convenios"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.nombre} ({self.tipo}) - {self.convenio.nombre}"


class DocumentoConvenio(models.Model):
    """
    Documentos y anexos legales formalmente almacenados y asociados a un Convenio SENA.
    """
    TIPO_DOC_CHOICES = [
        ('Documento del convenio', 'Documento del convenio'),
        ('Acta', 'Acta'),
        ('Certificación', 'Certificación'),
        ('Documento institucional', 'Documento institucional'),
        ('Otros', 'Otros'),
    ]

    convenio = models.ForeignKey(
        ConvenioSENA,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name="Convenio Asociado"
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Documento")
    archivo = models.FileField(upload_to='convenios/documentos/%Y/%m/', verbose_name="Archivo Digital")
    tipo = models.CharField(max_length=50, choices=TIPO_DOC_CHOICES, default='Documento del convenio', verbose_name="Tipo de Documento")
    fecha_carga = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Carga")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del Documento")
    usuario_carga = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_convenios_sena',
        verbose_name="Usuario que cargó el documento"
    )

    class Meta:
        verbose_name = "Documento de Convenio"
        verbose_name_plural = "Documentos de Convenios"
        ordering = ['-fecha_carga']

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    @property
    def extension(self):
        if self.archivo and self.archivo.name:
            return self.archivo.name.split('.')[-1].upper()
        return "ARCHIVO"
