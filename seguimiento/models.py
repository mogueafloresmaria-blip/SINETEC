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


class SolicitudSecretaria(models.Model):
    """
    Canal formal para que los aprendices e instructores radiquen solicitudes
    y trámites académicos/administrativos ante la Secretaría del SENA.
    """
    CATEGORIAS_SOLICITUD = [
        ('Academica', 'Académica (Novedades de formación)'),
        ('Certificacion', 'Certificación y Paz y Salvo'),
        ('Matricula', 'Matrícula y Traslados'),
        ('Ficha', 'Cambio o Novedad de Ficha'),
        ('Documentacion', 'Entrega o Solicitud de Documentación'),
        ('Horario', 'Ajuste de Horario / Ambientes'),
        ('Novedad', 'Novedad de Deserción / Aplazamiento'),
        ('Otra', 'Otra Consulta Institucional'),
    ]

    PRIORIDADES_SOLICITUD = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    ESTADOS_SOLICITUD = [
        ('ENVIADA', 'Enviada (Pendiente de Radicación)'),
        ('RECIBIDA', 'Recibida por Secretaría'),
        ('EN_REVISION', 'En Revisión / Trámite'),
        ('RESPONDIDA', 'Respondida'),
        ('CERRADA', 'Cerrada / Finalizada'),
    ]

    aprendiz = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitudes_secretaria',
        verbose_name="Aprendiz Solicitante"
    )
    ficha = models.ForeignKey(
        Ficha,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_secretaria',
        verbose_name="Ficha Relacionada"
    )
    asunto = models.CharField(
        max_length=200,
        verbose_name="Asunto de la Solicitud"
    )
    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS_SOLICITUD,
        default='Academica',
        verbose_name="Categoría del Trámite"
    )
    prioridad = models.CharField(
        max_length=20,
        choices=PRIORIDADES_SOLICITUD,
        default='Media',
        verbose_name="Prioridad"
    )
    mensaje = models.TextField(
        verbose_name="Descripción Detallada de la Solicitud"
    )
    archivo_adjunto = models.FileField(
        upload_to='solicitudes_secretaria/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Documento o Soporte Adjunto (PDF/Imagen)"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_SOLICITUD,
        default='ENVIADA',
        verbose_name="Estado de la Solicitud"
    )
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='solicitudes_atendidas',
        verbose_name="Funcionario Responsable (Secretaría/Coordinación)"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )

    class Meta:
        verbose_name = "Solicitud a Secretaría"
        verbose_name_plural = "Solicitudes a Secretaría"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.asunto} - {self.aprendiz.get_full_name() or self.aprendiz.username}"


class RespuestaSolicitud(models.Model):
    """
    Historial de mensajes, respuestas y seguimiento cruzado entre el aprendiz
    y los funcionarios de Secretaría o Coordinación respecto a una solicitud.
    """
    solicitud = models.ForeignKey(
        SolicitudSecretaria,
        on_delete=models.CASCADE,
        related_name='respuestas',
        verbose_name="Solicitud Asociada"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='respuestas_solicitud',
        verbose_name="Autor de la Respuesta"
    )
    mensaje = models.TextField(
        verbose_name="Contenido de la Respuesta"
    )
    archivo_adjunto = models.FileField(
        upload_to='respuestas_secretaria/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Documento Adjunto de Respuesta"
    )
    fecha_respuesta = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora de Respuesta"
    )

    class Meta:
        verbose_name = "Respuesta a Solicitud"
        verbose_name_plural = "Respuestas a Solicitudes"
        ordering = ['fecha_respuesta']

    def __str__(self):
        return f"Respuesta de {self.usuario.username} a solicitud #{self.solicitud.id} el {self.fecha_respuesta.strftime('%d/%m/%Y %H:%M')}"


class Notificacion(models.Model):
    """
    Notificaciones del sistema para aprendices, instructores y administrativos
    generadas automáticamente por eventos formativos clave.
    """
    TIPOS = [
        ('info', 'Información General'),
        ('success', 'Éxito / Aprobación'),
        ('warning', 'Atención / Alerta'),
        ('danger', 'Urgente / Deficiente'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name="Usuario Destinatario"
    )
    titulo = models.CharField(
        max_length=160,
        verbose_name="Título de la Notificación"
    )
    mensaje = models.TextField(
        verbose_name="Mensaje Detallado"
    )
    enlace = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name="Enlace de Acción Directa"
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default='info',
        verbose_name="Tipo de Notificación"
    )
    leida = models.BooleanField(
        default=False,
        verbose_name="¿Notificación Leída?"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Notificación"
    )

    class Meta:
        verbose_name = "Notificación Institucional"
        verbose_name_plural = "Notificaciones Institucionales"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} -> {self.usuario.username} ({'Leída' if self.leida else 'Nueva'})"


class RegistroAuditoria(models.Model):
    """
    Trazabilidad inmutable de acciones críticas realizadas en SINETEC
    (evaluaciones, creación de evidencias, solicitudes, matrículas).
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registros_auditoria',
        verbose_name="Usuario Ejecutor"
    )
    accion = models.CharField(
        max_length=160,
        verbose_name="Acción Realizada"
    )
    modulo = models.CharField(
        max_length=80,
        verbose_name="Módulo Institucional"
    )
    detalles = models.TextField(
        blank=True,
        default='',
        verbose_name="Detalles Técnicos y Datos Modificados"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP de Origen"
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora de la Acción"
    )

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-fecha']

    def __str__(self):
        usr = self.usuario.username if self.usuario else 'Sistema'
        return f"[{self.fecha.strftime('%d/%m/%Y %H:%M')}] {usr} · {self.modulo} · {self.accion}"

    @classmethod
    def registrar(cls, usuario, modulo, accion, detalles='', request=None):
        ip = None
        if request:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            if ip and ',' in ip:
                ip = ip.split(',')[0].strip()
        user_obj = usuario if (usuario and getattr(usuario, 'is_authenticated', False)) else None
        return cls.objects.create(
            usuario=user_obj,
            modulo=modulo,
            accion=accion,
            detalles=detalles,
            ip_address=ip or '127.0.0.1'
        )


class CompromisoFormativo(models.Model):
    """
    Compromiso individual o colectivo con responsable, fechas de cumplimiento,
    evidencias y estados del ciclo formativo SENA.
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('EN_PROCESO', 'En Proceso'),
        ('CUMPLIDO', 'Cumplido'),
        ('VENCIDO', 'Vencido'),
    ]

    bitacora = models.ForeignKey(
        BitacoraSeguimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compromisos_asociados',
        verbose_name="Bitácora de Origen (Opcional)"
    )
    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='compromisos_formativos',
        verbose_name="Aprendiz Responsable"
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='compromisos_asignados',
        verbose_name="Instructor Verificador"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título del Compromiso")
    descripcion = models.TextField(verbose_name="Descripción y Plan de Acción")
    fecha_limite = models.DateField(verbose_name="Fecha Límite")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', verbose_name="Estado")
    evidencia_cumplimiento = models.FileField(
        upload_to='compromisos_evidencias/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Evidencia de Cumplimiento (PDF / Imagen)"
    )
    observaciones_verificacion = models.TextField(blank=True, verbose_name="Retroalimentación del Instructor")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compromiso Formativo"
        verbose_name_plural = "Compromisos Formativos"
        ordering = ['fecha_limite']

    def __str__(self):
        return f"{self.titulo} - {self.matricula.aprendiz.get_full_name()} [{self.get_estado_display()}]"

    def esta_vencido(self):
        from django.utils import timezone
        return self.estado in ['PENDIENTE', 'EN_PROCESO'] and self.fecha_limite < timezone.localdate()


class ConfiguracionAlertas(models.Model):
    """
    Parámetros configurables del Motor de Alertas Tempranas del Centro.
    """
    umbral_asistencia_preventiva = models.DecimalField(max_digits=5, decimal_places=2, default=80.0, verbose_name="% Asistencia Alerta Preventiva")
    umbral_asistencia_critica = models.DecimalField(max_digits=5, decimal_places=2, default=60.0, verbose_name="% Asistencia Alerta Crítica")
    max_evidencias_pendientes = models.PositiveIntegerField(default=3, verbose_name="Máx. Evidencias Pendientes")
    dias_inactividad_alerta = models.PositiveIntegerField(default=10, verbose_name="Días de Inactividad para Alerta")
    actualizado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Alertas Tempranas"
        verbose_name_plural = "Configuraciones de Alertas Tempranas"

    def __str__(self):
        return f"Configuración Alertas (Asist: {self.umbral_asistencia_preventiva}% / Crít: {self.umbral_asistencia_critica}%)"


class CasoAlertaTemprana(models.Model):
    """
    Expediente estructurado de intervención para acompañamiento formativo y prevención de deserción.
    Flujo: ALERTA -> REVISION -> ASIGNACION -> INTERVENCION -> COMPROMISO -> SEGUIMIENTO -> RESULTADO -> CIERRE
    """
    ESTADOS_CASO = [
        ('ALERTA', 'Alerta Generada'),
        ('REVISION', 'En Revisión'),
        ('ASIGNACION', 'Asignación de Responsable'),
        ('INTERVENCION', 'Intervención / Citación'),
        ('COMPROMISO', 'Plan de Compromisos'),
        ('SEGUIMIENTO', 'En Seguimiento'),
        ('RESULTADO', 'Evaluación de Resultados'),
        ('CERRADO', 'Caso Cerrado'),
    ]

    TIPOS_ALERTA = [
        ('inasistencia', 'Inasistencia Reiterada'),
        ('academica', 'Rendimiento Académico RAP'),
        ('evidencias', 'Evidencias Formativas Pendientes'),
        ('compromiso_vencido', 'Compromiso Vencido sin Verificar'),
        ('multidisciplinaria', 'Riesgo Integral Multi-factor'),
    ]

    NIVELES_RIESGO = [
        ('BAJO', 'Bajo'),
        ('MEDIO', 'Medio / Preventivo'),
        ('ALTO', 'Alto / Crítico'),
    ]

    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='casos_alerta',
        verbose_name="Aprendiz Vinculado"
    )
    tipo_alerta = models.CharField(max_length=40, choices=TIPOS_ALERTA, verbose_name="Tipo de Alerta")
    nivel_riesgo = models.CharField(max_length=20, choices=NIVELES_RIESGO, default='MEDIO', verbose_name="Nivel de Riesgo")
    puntuacion_riesgo = models.DecimalField(max_digits=5, decimal_places=1, default=50.0, verbose_name="Puntuación de Riesgo (%)")
    factores_detectados = models.TextField(verbose_name="Factores Explicables Detectados")
    estado = models.CharField(max_length=25, choices=ESTADOS_CASO, default='ALERTA', verbose_name="Fase del Flujo")
    responsable = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='casos_alerta_asignados',
        verbose_name="Funcionario / Instructor Responsable"
    )
    plan_accion = models.TextField(blank=True, verbose_name="Plan de Acción e Intervención")
    resultado_final = models.TextField(blank=True, verbose_name="Resultado del Caso")
    fecha_deteccion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Caso de Alerta Temprana"
        verbose_name_plural = "Casos de Alerta Temprana"
        ordering = ['-fecha_deteccion']

    def __str__(self):
        return f"Caso #{self.id} · {self.matricula.aprendiz.get_full_name()} [{self.get_estado_display()}]"


class EmpresaConvenio(models.Model):
    """
    Empresas aliadas y patrocinadoras donde los aprendices realizan su Etapa Productiva.
    """
    razon_social = models.CharField(max_length=200, verbose_name="Razón Social")
    nit = models.CharField(max_length=30, unique=True, verbose_name="NIT / Identificación Tributaria")
    representante_legal = models.CharField(max_length=150, blank=True, verbose_name="Representante Legal")
    contacto_nombre = models.CharField(max_length=150, verbose_name="Persona de Contacto")
    contacto_cargo = models.CharField(max_length=100, blank=True, verbose_name="Cargo de Contacto")
    contacto_email = models.EmailField(verbose_name="Correo Electrónico")
    contacto_telefono = models.CharField(max_length=30, verbose_name="Teléfono")
    direccion = models.CharField(max_length=255, blank=True, verbose_name="Dirección de la Sede")
    municipio = models.CharField(max_length=100, default='Santa Marta', verbose_name="Municipio")
    activa = models.BooleanField(default=True, verbose_name="¿Convenio Activo?")
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Empresa en Convenio"
        verbose_name_plural = "Empresas en Convenio"
        ordering = ['razon_social']

    def __str__(self):
        return f"{self.razon_social} (NIT: {self.nit})"


class EtapaProductiva(models.Model):
    """
    Gestión formal de la Etapa Productiva SENA para aprendices de Media Técnica.
    """
    MODALIDADES = [
        ('Contrato de Aprendizaje', 'Contrato de Aprendizaje'),
        ('Pasantia', 'Pasantía Institucional / Empresarial'),
        ('Vinculo Laboral', 'Vínculo Laboral o Contractual'),
        ('Proyecto Productivo', 'Proyecto Productivo de Innovación'),
        ('Monitoria', 'Monitoría Académica SENA'),
    ]

    ESTADOS = [
        ('POR_INICIAR', 'Por Iniciar / En Trámite de Convenio'),
        ('EN_DESARROLLO', 'En Desarrollo Activo'),
        ('FINALIZADA', 'Finalizada y Aprobada'),
        ('NOVEDAD', 'Novedad de Aplazamiento o Cancelación'),
    ]

    matricula = models.OneToOneField(
        Matricula,
        on_delete=models.CASCADE,
        related_name='etapa_productiva',
        verbose_name="Aprendiz en Formación"
    )
    empresa = models.ForeignKey(
        EmpresaConvenio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aprendices_vinculados',
        verbose_name="Empresa Patrocinadora / Co-formadora"
    )
    modalidad = models.CharField(
        max_length=40,
        choices=MODALIDADES,
        default='Contrato de Aprendizaje',
        verbose_name="Modalidad SENA"
    )
    instructor_seguimiento = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='aprendices_seguimiento_productivo',
        verbose_name="Instructor de Seguimiento Asignado"
    )
    tutor_empresarial = models.CharField(max_length=150, blank=True, verbose_name="Nombre del Tutor Empresarial")
    tutor_cargo = models.CharField(max_length=100, blank=True, verbose_name="Cargo del Tutor")
    tutor_email = models.EmailField(blank=True, verbose_name="Correo del Tutor")
    tutor_telefono = models.CharField(max_length=30, blank=True, verbose_name="Teléfono del Tutor")
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(null=True, blank=True, verbose_name="Fecha Estimada de Culminación")
    estado = models.CharField(max_length=25, choices=ESTADOS, default='POR_INICIAR', verbose_name="Estado de la Etapa")
    observaciones = models.TextField(blank=True, verbose_name="Observaciones de la Coordinación")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Etapa Productiva de Aprendiz"
        verbose_name_plural = "Etapas Productivas de Aprendices"
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.matricula.aprendiz.get_full_name()} · {self.modalidad} ({self.get_estado_display()})"


class BitacoraEtapaProductiva(models.Model):
    """
    Registro de visitas de supervisión y seguimiento concertado a la Etapa Productiva.
    """
    VISITAS = [
        (1, 'Visita Inicial (Concertación de Plan de Trabajo)'),
        (2, 'Visita Intermedia (Evaluación Parcial de Desempeño)'),
        (3, 'Visita Final (Evaluación y Cierre de Etapa Productiva)'),
    ]

    CONCEPTOS = [
        ('SATISFACTORIO', 'Cumplimiento Satisfactorio'),
        ('POR_MEJORAR', 'Requiere Plan de Mejoramiento'),
        ('DEFICIENTE', 'No Cumple / Novedad'),
    ]

    etapa_productiva = models.ForeignKey(
        EtapaProductiva,
        on_delete=models.CASCADE,
        related_name='bitacoras',
        verbose_name="Expediente de Etapa Productiva"
    )
    numero_visita = models.PositiveSmallIntegerField(choices=VISITAS, default=1, verbose_name="Número de Visita")
    fecha_visita = models.DateField(verbose_name="Fecha de la Visita")
    instructor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Instructor Evaluador")
    actividades_desarrolladas = models.TextField(verbose_name="Actividades Técnicas Desarrolladas por el Aprendiz")
    concepto_evaluativo = models.CharField(max_length=25, choices=CONCEPTOS, default='SATISFACTORIO', verbose_name="Concepto de la Visita")
    observaciones_tutor = models.TextField(blank=True, verbose_name="Observaciones del Tutor Empresarial")
    observaciones_instructor = models.TextField(blank=True, verbose_name="Recomendaciones del Instructor SENA")
    acta_soporte_pdf = models.FileField(
        upload_to='etapa_productiva_actas/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Acta de Visita Firmada (Formato F023 SENA)"
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bitácora de Etapa Productiva"
        verbose_name_plural = "Bitácoras de Etapa Productiva"
        ordering = ['etapa_productiva', 'numero_visita']

    def __str__(self):
        return f"Visita {self.numero_visita} · {self.etapa_productiva.matricula.aprendiz.get_full_name()} ({self.fecha_visita})"