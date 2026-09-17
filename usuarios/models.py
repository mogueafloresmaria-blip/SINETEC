"""
Aplicación: usuarios
Modelos: Rol, PerfilUsuario
Reglas de Negocio Asociadas: RN-001 (Unicidad de Documento), RN-008 (Borrado Lógico)
"""

from io import BytesIO
import uuid

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Rol(models.Model):
    """
    Representa los perfiles de seguridad institucional en SINETEC.
    Ejemplos: Administrador, Coordinador, Instructor SENA, Docente I.E., Estudiante.
    """
    nombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre del Rol"
    )
    descripcion = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Descripción de Funciones"
    )

    class Meta:
        verbose_name = "Rol de Usuario"
        verbose_name_plural = "Roles de Usuario"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PerfilUsuario(models.Model):
    """
    Extensión del usuario estándar de Django para almacenar datos institucionales,
    documento de identidad y rol asignado en la Media Técnica.
    """
    TIPO_DOC_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PEP', 'Permiso Especial de Permanencia'),
        ('PPT', 'Permiso por Protección Temporal'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Cuenta de Usuario"
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='usuarios',
        verbose_name="Rol Institucional",
        null=True,
        blank=True
    )
    tipo_documento = models.CharField(
        max_length=5,
        choices=TIPO_DOC_CHOICES,
        default='CC',
        verbose_name="Tipo de Documento"
    )
    # RN-001: No pueden existir dos personas con el mismo número de documento
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Número de Documento"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono de Contacto"
    )
    # RN-008: Borrado lógico / estado de la cuenta
    esta_activo = models.BooleanField(
        default=True,
        verbose_name="¿Cuenta Activa?"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    qr_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='Token del carnet QR',
    )
    qr_code = models.ImageField(
        upload_to='carnets_qr/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Código QR del carnet',
    )
    qr_rotacion = models.DateField(blank=True, null=True, editable=False, verbose_name='Día de rotación QR')

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        ordering = ['usuario__last_name', 'usuario__first_name']

    def __str__(self):
        nombre_completo = self.usuario.get_full_name() or self.usuario.username
        rol_nombre = self.rol.nombre if self.rol else "Sin Rol"
        return f"{nombre_completo} ({rol_nombre} - {self.numero_documento})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.utils import timezone
        if self.rol and self.rol.nombre == 'Estudiante' and (not self.qr_code or self.qr_rotacion != timezone.localdate()):
            self.qr_rotacion = timezone.localdate()
            self.generar_qr()
            super().save(update_fields=['qr_code', 'qr_rotacion'])

    def generar_qr(self):
        base_url = getattr(settings, 'QR_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
        payload = f'{base_url}/estudiantes/qr/{self.qr_token}/?dia={self.qr_rotacion}'
        imagen = qrcode.make(payload)
        buffer = BytesIO()
        imagen.save(buffer, format='PNG')
        self.qr_code.save(
            f'{self.qr_token}.png',
            ContentFile(buffer.getvalue()),
            save=False,
        )

    def asegurar_qr(self):
        if self.rol and self.rol.nombre == 'Estudiante' and not self.qr_code:
            self.save()


@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal automática para asegurar que cada Usuario de Django tenga su Perfil correspondiente.
    """
    if created:
        PerfilUsuario.objects.get_or_create(
            usuario=instance,
            defaults={'numero_documento': f"DOC-{instance.id}-{instance.username[:10]}"}
        )
from django.db import models
from django.contrib.auth.models import User

class FichaSena(models.Model):
    numero_ficha = models.CharField(max_length=20, unique=True, verbose_name="Número de Ficha")
    programa = models.CharField(max_length=150, verbose_name="Nombre del Programa (Técnico/Tecnólogo)")
    jornada = models.CharField(max_length=50, choices=[('Diurna', 'Diurna'), ('Nocturna', 'Nocturna'), ('Mixta', 'Mixta')], default='Diurna')
    
    def __str__(self):
        return f"Ficha {self.numero_ficha} - {self.programa}"


class ResultadoAprendizaje(models.Model):
    """RAP (Resultado de Aprendizaje) asociado a una competencia del programa SENA"""
    ficha = models.ForeignKey(FichaSena, on_delete=models.CASCADE, related_name='raps')
    codigo = models.CharField(max_length=50, verbose_name="Código RAP")
    descripcion = models.TextField(verbose_name="Descripción del Resultado de Aprendizaje")
    
    def __str__(self):
        return f"RAP {self.codigo} (Ficha {self.ficha.numero_ficha})"


class EvidenciaTaller(models.Model):
    """Guía o Taller asignado al aprendiz"""
    rap = models.ForeignKey(ResultadoAprendizaje, on_delete=models.CASCADE, related_name='evidencias')
    titulo = models.CharField(max_length=200, verbose_name="Título del Taller / Evidencia")
    descripcion = models.TextField(verbose_name="Instrucciones de la Guía de Aprendizaje")
    fecha_limite = models.DateTimeField(verbose_name="Fecha y Hora Límite de Entrega")
    
    def __str__(self):
        return f"{self.titulo} - RAP: {self.rap.codigo}"


class CalificacionEvidencia(models.Model):
    """Juicio evaluativo SENA (Aprobado 'A' o Deficiente 'D')"""
    ESTADOS_JUICIO = [
        ('A', 'Aprobado (A)'),
        ('D', 'Deficiente (D)'),
        ('PENDIENTE', 'Pendiente de Calificar'),
    ]
    
    evidencia = models.ForeignKey(EvidenciaTaller, on_delete=models.CASCADE, related_name='calificaciones')
    aprendiz = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'perfil__rol__nombre': 'Estudiante'})
    archivo_entregado = models.FileField(upload_to='talleres_aprendices/', blank=True, null=True, verbose_name="Archivo del Taller")
    fecha_entrega = models.DateTimeField(auto_now_add=True)
    
    juicio_evaluativo = models.CharField(max_length=10, choices=ESTADOS_JUICIO, default='PENDIENTE', verbose_name="Juicio Evaluativo")
    observaciones = models.TextField(blank=True, null=True, verbose_name="Retroalimentación del Instructor")
    
    class Meta:
        unique_together = ('evidencia', 'aprendiz')

    def __str__(self):
        return f"Aprendiz {self.aprendiz.get_full_name()} - {self.evidencia.titulo} [{self.juicio_evaluativo}]"