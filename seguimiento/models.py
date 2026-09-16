"""
Aplicación: seguimiento
Modelo: BitacoraSeguimiento
Reglas de Negocio Asociadas: RN-005 (Restricción por Ficha Asignada), RN-006 (Compromisos Obligatorios)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from academico.models import Ficha, Matricula


class AsistenciaAprendiz(models.Model):
    """Registro de asistencia de un aprendiz en una sesión de su ficha."""
    ESTADOS = [
        ('P', 'Presente'),
        ('A', 'Ausente'),
        ('J', 'Ausencia justificada'),
    ]

    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name='Aprendiz matriculado',
    )
    fecha = models.DateField(verbose_name='Fecha de la sesión')
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P', verbose_name='Estado')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    registrado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='asistencias_registradas',
        verbose_name='Registrado por',
    )

    class Meta:
        verbose_name = 'Asistencia de aprendiz'
        verbose_name_plural = 'Asistencias de aprendices'
        ordering = ['-fecha']
        constraints = [
            models.UniqueConstraint(fields=['matricula', 'fecha'], name='asistencia_unica_por_fecha'),
        ]

    def __str__(self):
        return f'{self.matricula} - {self.fecha} ({self.get_estado_display()})'


class BitacoraSeguimiento(models.Model):
    """
    Registro formal de visitas presenciales o virtuales a las Instituciones Educativas,
    donde el instructor SENA documenta el avance, dificultades y compromisos de la Media Técnica.
    """
    TIPO_SEGUIMIENTO_CHOICES = [
        ('Presencial Aula', 'Visita Presencial en Aula de Clase'),
        ('Revision Taller', 'Revisión Presencial de Ambientes / Taller'),
        ('Reunion Colegio', 'Reunión con Rectoría / Docente Enlace'),
        ('Virtual', 'Sesión de Acompañamiento Virtual'),
        ('Comite', 'Comité de Seguimiento Formativo'),
    ]

    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.CASCADE,
        related_name='seguimientos',
        verbose_name="Ficha de Media Técnica",
        help_text="Ficha técnica a la cual se realizó el acompañamiento."
    )
    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seguimientos_individuales',
        verbose_name="Aprendiz Específico (Opcional)",
        help_text="Dejar vacío si el seguimiento fue general para todo el grupo de la ficha."
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='seguimientos_registrados',
        verbose_name="Instructor que Realizó la Visita"
    )
    fecha_visita = models.DateField(
        verbose_name="Fecha de la Visita o Sesión"
    )
    tipo_seguimiento = models.CharField(
        max_length=30,
        choices=TIPO_SEGUIMIENTO_CHOICES,
        default='Presencial Aula',
        verbose_name="Tipo de Seguimiento"
    )
    observaciones = models.TextField(
        verbose_name="Diagnóstico y Observaciones Pedagógicas / Técnicas"
    )
    # RN-006: Exigencia de compromisos y fecha de verificación
    compromisos = models.TextField(
        blank=True,
        null=True,
        verbose_name="Compromisos y Plan de Acción Acordado"
    )
    fecha_verificacion = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha Límite para Verificar Cumplimiento de Compromisos"
    )
    archivo_adjunto = models.FileField(
        upload_to='actas_seguimiento/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Acta de Visita Firmada o Soporte Escaneado (PDF/Imagen)"
    )
    firma_instructor = models.ImageField(
        upload_to='firmas_actas/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Firma del instructor SENA',
    )
    firma_docente_enlace = models.ImageField(
        upload_to='firmas_actas/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Firma del docente enlace',
    )
    latitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='Latitud GPS de la visita',
    )
    longitud = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name='Longitud GPS de la visita',
    )
    precision_gps = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Precisión GPS en metros',
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Marca de Tiempo del Registro (Inmutable)"
    )

    class Meta:
        verbose_name = "Bitácora de Seguimiento"
        verbose_name_plural = "Bitácoras de Seguimiento"
        ordering = ['-fecha_visita', '-fecha_registro']

    def __str__(self):
        destino = self.matricula.aprendiz.get_full_name() if self.matricula else f"Grupo Ficha {self.ficha.codigo_ficha}"
        return f"Seguimiento {self.fecha_visita} - {destino} ({self.tipo_seguimiento})"

    def clean(self):
        """
        Validación de la regla RN-006:
        Si se registran compromisos, debe especificarse una fecha de verificación de los mismos.
        """
        super().clean()
        if self.compromisos and not self.fecha_verificacion:
            raise ValidationError({
                'fecha_verificacion': "Si se establecen compromisos de mejora, es obligatorio indicar una fecha de verificación (RN-006)."
            })


class MensajeSeguimiento(models.Model):
    """
    Comunicación interna y mensajes cruzados entre instructores y aprendices
    relacionados directamente con un caso o bitácora de seguimiento.
    """
    bitacora = models.ForeignKey(
        BitacoraSeguimiento,
        on_delete=models.CASCADE,
        related_name='mensajes',
        verbose_name="Bitácora / Caso de Seguimiento"
    )
    remitente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        verbose_name="Remitente"
    )
    mensaje = models.TextField(
        verbose_name="Contenido del Mensaje o Aviso"
    )
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora de Envio"
    )

    class Meta:
        verbose_name = "Mensaje de Seguimiento"
        verbose_name_plural = "Mensajes de Seguimiento"
        ordering = ['fecha_envio']

    def __str__(self):
        return f"Mensaje de {self.remitente.username} el {self.fecha_envio.strftime('%d/%m/%Y %H:%M')}"