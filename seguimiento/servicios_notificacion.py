import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
from seguimiento.models import Notificacion

logger = logging.getLogger(__name__)

# Paleta y estilo institucional EDUNOVA
COLOR_PRINCIPAL = '#007F7B'
COLOR_OSCURO = '#004D4A'
COLOR_SECUNDARIO = '#006B68'
COLOR_FONDO = '#F4FAF9'


def generar_plantilla_email_html(nombre_destinatario, titulo, mensaje, enlace='', tipo='info'):
    """Genera plantilla de correo HTML responsiva y elegante con la identidad visual de EDUNOVA."""
    color_badge = '#0284c7'
    texto_badge = 'Información'
    if tipo == 'success':
        color_badge = '#16a34a'
        texto_badge = 'Aprobado / Novedad'
    elif tipo == 'warning':
        color_badge = '#d97706'
        texto_badge = 'Atención Requerida'
    elif tipo == 'danger':
        color_badge = '#dc2626'
        texto_badge = 'Importante'

    boton_accion = ""
    if enlace:
        url_completa = enlace
        if enlace.startswith('/'):
            url_completa = f"https://edunova.edu.co{enlace}"
        boton_accion = f"""
        <div style="margin: 28px 0; text-align: center;">
            <a href="{url_completa}" style="background: linear-gradient(135deg, {COLOR_PRINCIPAL} 0%, {COLOR_OSCURO} 100%); color: #ffffff; text-decoration: none; padding: 13px 32px; border-radius: 50px; font-weight: bold; font-size: 15px; display: inline-block; box-shadow: 0 4px 12px rgba(0, 127, 123, 0.25);">
                Acceder en EDUNOVA &rarr;
            </a>
        </div>
        """

    fecha_actual_str = timezone.localtime().strftime("%d/%m/%Y %I:%M %p")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} - EDUNOVA</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1e293b;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #f1f5f9; padding: 30px 15px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;">
                    
                    <!-- ENCABEZADO INSTITUCIONAL -->
                    <tr>
                        <td style="background: linear-gradient(135deg, {COLOR_PRINCIPAL} 0%, {COLOR_OSCURO} 100%); padding: 32px 30px; text-align: center; color: #ffffff;">
                            <div style="font-size: 26px; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 4px;">
                                EDUNOVA
                            </div>
                            <div style="font-size: 13px; color: #DDF7F5; font-weight: 500; letter-spacing: 0.3px;">
                                Plataforma de Gestión Académica Institucional
                            </div>
                        </td>
                    </tr>

                    <!-- CUERPO PRINCIPAL -->
                    <tr>
                        <td style="padding: 35px 32px 25px 32px;">
                            
                            <div style="margin-bottom: 20px;">
                                <span style="display: inline-block; background-color: {color_badge}; color: #ffffff; font-size: 11px; font-weight: 700; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; letter-spacing: 0.5px;">
                                    {texto_badge}
                                </span>
                            </div>

                            <h2 style="font-size: 20px; font-weight: 700; color: #0f172a; margin-top: 0; margin-bottom: 14px; line-height: 1.35;">
                                {titulo}
                            </h2>

                            <p style="font-size: 15px; color: #475569; margin: 0 0 18px 0; line-height: 1.6;">
                                Estimado(a) <strong>{nombre_destinatario}</strong>,
                            </p>

                            <div style="background-color: {COLOR_FONDO}; border-left: 4px solid {COLOR_PRINCIPAL}; border-radius: 0 8px 8px 0; padding: 18px 20px; margin-bottom: 20px; font-size: 14.5px; color: #1e293b; line-height: 1.65; white-space: pre-line;">
                                {mensaje}
                            </div>

                            {boton_accion}

                            <p style="font-size: 12.5px; color: #64748b; margin-top: 25px; line-height: 1.5; border-top: 1px solid #f1f5f9; padding-top: 18px;">
                                💡 Puedes gestionar tus actividades, materiales, comunicados y calificaciones iniciando sesión en tu panel oficial de EDUNOVA desde cualquier dispositivo.
                            </p>
                        </td>
                    </tr>

                    <!-- PIE DE CORREO -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 22px 30px; text-align: center; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                            <div style="font-weight: 600; color: #64748b; margin-bottom: 4px;">
                                Sistema Institucional EDUNOVA
                            </div>
                            <div>
                                Notificación automática generada el {fecha_actual_str}.<br>
                                Por favor no responda directamente a este correo automático.
                            </div>
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
    return html


def enviar_notificacion_automatica(usuario, titulo, mensaje, enlace='', tipo='info', enviar_email=True, asunto_email=None):
    """
    Crea la notificación interna en la plataforma y envía correo electrónico automático si el usuario tiene email registrado.
    Maneja excepciones de forma segura para no afectar la transacción principal.
    """
    if not usuario or not isinstance(usuario, User):
        return None

    notif = None
    try:
        # 1. Registrar notificación en la base de datos de la plataforma
        notif = Notificacion.objects.create(
            usuario=usuario,
            titulo=str(titulo)[:160],
            mensaje=str(mensaje),
            enlace=str(enlace or ''),
            tipo=tipo
        )
        # Invalidar caché de contador de campana
        cache.delete(f'edunova_notif_u_{usuario.pk}')
    except Exception as e:
        logger.error(f"[EDUNOVA NOTIF] Error creando Notificacion para {usuario.username}: {e}")

    # 2. Envío de correo electrónico automático por SMTP
    if enviar_email and usuario.email and '@' in usuario.email:
        try:
            nombre = usuario.get_full_name() or usuario.username
            asunto = asunto_email or f"[EDUNOVA] {titulo}"
            html_content = generar_plantilla_email_html(
                nombre_destinatario=nombre,
                titulo=titulo,
                mensaje=mensaje,
                enlace=enlace,
                tipo=tipo
            )
            msg = EmailMultiAlternatives(
                subject=asunto,
                body=f"Hola {nombre},\n\n{titulo}\n\n{mensaje}\n\nAcceder: {enlace}\n\nEDUNOVA",
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'EDUNOVA <notificaciones@edunova.edu.co>'),
                to=[usuario.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
            logger.info(f"[EDUNOVA NOTIF] Correo enviado a {usuario.email} para evento '{titulo}'")
        except Exception as e:
            logger.warning(f"[EDUNOVA NOTIF] No se pudo enviar correo a {usuario.email}: {e}")

    return notif


def notificar_usuarios_masivo(usuarios, titulo, mensaje, enlace='', tipo='info', enviar_email=True, notificar_acudientes=True):
    """
    Envía notificaciones internas y correos a una lista de usuarios (ej: estudiantes de un grado/grupo).
    Opcionalmente notifica también a los acudientes vinculados.
    """
    from usuarios.models import FamiliaAcudiente
    usuarios_unicos = list({u.id: u for u in usuarios if u and isinstance(u, User)}.values())
    notificaciones_creadas = []

    for u in usuarios_unicos:
        n = enviar_notificacion_automatica(
            usuario=u,
            titulo=titulo,
            mensaje=mensaje,
            enlace=enlace,
            tipo=tipo,
            enviar_email=enviar_email
        )
        if n:
            notificaciones_creadas.append(n)

        # Notificar también a los padres / acudientes vinculados si aplica
        if notificar_acudientes:
            try:
                perfil_doc = getattr(getattr(u, 'perfil', None), 'numero_documento', None) or u.username
                familias = FamiliaAcudiente.objects.filter(
                    Q(estudiantes=u) | Q(documento=perfil_doc) | (Q(email__iexact=u.email) & ~Q(email=''))
                ).distinct()
                for fam in familias:
                    fam_user = User.objects.filter(Q(username=fam.documento) | (Q(email__iexact=fam.email) & ~Q(email=''))).first()
                    if fam_user and fam_user.id != u.id:
                        msg_acudiente = f"Novedad para tu acudido(a) {u.get_full_name() or u.username}:\n\n{mensaje}"
                        enviar_notificacion_automatica(
                            usuario=fam_user,
                            titulo=f"[Acudiente] {titulo}",
                            mensaje=msg_acudiente,
                            enlace=enlace,
                            tipo=tipo,
                            enviar_email=enviar_email
                        )
            except Exception as e:
                logger.warning(f"[EDUNOVA NOTIF] Error notificando acudientes de {u.username}: {e}")

    return len(notificaciones_creadas)
