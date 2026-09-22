from seguimiento.models import Notificacion, BitacoraSeguimiento
from academico.models import Ficha
from usuarios.models import ConfiguracionColegio
from django.utils import timezone
from datetime import timedelta


def notificaciones_context(request):
    """
    Context processor para alimentar la campana de notificaciones en la barra superior (topbar)
    y la identidad escolar del colegio en toda la plataforma.
    """
    try:
        colegio = ConfiguracionColegio.get_solo()
    except Exception:
        colegio = None

    if not request.user.is_authenticated:
        return {
            'notificaciones_campana': [],
            'num_notificaciones_no_leidas': 0,
            'tiene_alertas_admin': False,
            'colegio': colegio,
        }

    user = request.user
    notificaciones_qs = Notificacion.objects.filter(usuario=user)
    no_leidas = notificaciones_qs.filter(leida=False).count()
    recientes = list(notificaciones_qs.order_by('-fecha_creacion')[:5])

    # Si es administrador, revisar alertas del sistema
    alertas_admin_count = 0
    rol_nombre = getattr(getattr(user, 'perfil', None), 'rol', None)
    rol_str = rol_nombre.nombre if rol_nombre else ''
    if user.is_superuser or 'Admin' in rol_str or 'Coordinador' in rol_str:
        hoy = timezone.localdate()
        vencen = Ficha.objects.filter(estado='En Ejecucion', fecha_fin__lte=hoy + timedelta(days=30), fecha_fin__gte=hoy).count()
        pend = BitacoraSeguimiento.objects.filter(estado='Pendiente').count()
        alertas_admin_count = vencen + pend

    total_badge = no_leidas if no_leidas > 0 else (alertas_admin_count if alertas_admin_count > 0 else 0)

    return {
        'notificaciones_campana': recientes,
        'num_notificaciones_no_leidas': total_badge,
        'tiene_alertas_admin': alertas_admin_count > 0,
        'colegio': colegio,
    }
