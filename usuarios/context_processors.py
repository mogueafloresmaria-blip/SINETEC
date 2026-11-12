from seguimiento.models import Notificacion, BitacoraSeguimiento
from academico.models import Ficha, Matricula
from usuarios.models import ConfiguracionColegio, FamiliaAcudiente
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Q
import re


def notificaciones_context(request):
    """
    Context processor optimizado con caché en memoria (LocMemCache).
    Alimenta la campana de notificaciones y la identidad escolar del colegio
    reduciendo las consultas a base de datos de 5 a 0 en la mayoría de peticiones.
    """
    # 1. Caché de identidad institucional y paleta de colores (5 minutos)
    cached_identidad = cache.get('edunova_colegio_identidad')
    if cached_identidad:
        colegio, tema_colores = cached_identidad
    else:
        try:
            colegio = ConfiguracionColegio.get_solo()
            tema_colores = colegio.paleta()
            cache.set('edunova_colegio_identidad', (colegio, tema_colores), timeout=300)
        except Exception:
            colegio = None
            tema_colores = dict(ConfiguracionColegio.COLORES_POR_DEFECTO)

    if not request.user.is_authenticated:
        return {
            'notificaciones_campana': [],
            'num_notificaciones_no_leidas': 0,
            'tiene_alertas_admin': False,
            'colegio': colegio,
            'tema_colores': tema_colores,
        }

    # 2. Caché para notificaciones de usuario (30 segundos por usuario)
    user = request.user
    cache_key_user = f'edunova_notif_u_{user.pk}'
    user_notif_data = cache.get(cache_key_user)

    if user_notif_data is None:
        rol_nombre = getattr(getattr(user, 'perfil', None), 'rol', None)
        rol_str = rol_nombre.nombre if rol_nombre else ''

        # Aislamiento por rol, grado y familia
        if any(r in rol_str for r in ['Familia', 'Acudiente']):
            doc_u = getattr(getattr(user, 'perfil', None), 'numero_documento', None) or user.username
            fa_qs = FamiliaAcudiente.objects.filter(
                Q(documento=doc_u) | Q(email__iexact=user.email) | Q(estudiantes__username=user.username)
            ).distinct()
            hijos_ids = set()
            for fa in fa_qs:
                hijos_ids.update(fa.estudiantes.values_list('id', flat=True))
            
            notificaciones_qs = Notificacion.objects.filter(
                Q(usuario=user) | Q(usuario_id__in=hijos_ids)
            ).distinct()

            # Obtener los grados de los hijos para evitar fugas de otros grados
            grados_hijos = set()
            if hijos_ids:
                mats = Matricula.objects.filter(aprendiz_id__in=hijos_ids, estado_formacion='En Formacion')
                for m in mats:
                    g_dig = ''.join(ch for ch in str(m.grado_escolar) if ch.isdigit())
                    if g_dig:
                        grados_hijos.add(g_dig)

            if grados_hijos:
                todos_grados = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'}
                otros_grados = todos_grados - grados_hijos
                for og in otros_grados:
                    notificaciones_qs = notificaciones_qs.exclude(
                        Q(titulo__iregex=rf'\bgrado\s*{og}\b') | Q(titulo__icontains=f'Grado {og}°')
                    )
        elif any(r in rol_str for r in ['Estudiante', 'Aprendiz', 'Alumno']):
            notificaciones_qs = Notificacion.objects.filter(usuario=user)
            mat = Matricula.objects.filter(aprendiz=user, estado_formacion='En Formacion').first()
            if mat and mat.grado_escolar:
                g_est = ''.join(ch for ch in str(mat.grado_escolar) if ch.isdigit())
                if g_est:
                    todos_grados = {'1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'}
                    otros_grados = todos_grados - {g_est}
                    for og in otros_grados:
                        notificaciones_qs = notificaciones_qs.exclude(
                            Q(titulo__iregex=rf'\bgrado\s*{og}\b') | Q(titulo__icontains=f'Grado {og}°')
                        )
        else:
            notificaciones_qs = Notificacion.objects.filter(usuario=user)

        no_leidas = notificaciones_qs.filter(leida=False).count()
        recientes = list(notificaciones_qs.order_by('-fecha_creacion')[:25])

        # Si es administrador o coordinador, revisar alertas operativas
        alertas_admin_count = 0
        if user.is_superuser or 'Admin' in rol_str or 'Coordinador' in rol_str:
            hoy = timezone.localdate()
            vencen = Ficha.objects.filter(estado='En Ejecucion', fecha_fin__lte=hoy + timedelta(days=30), fecha_fin__gte=hoy).count()
            pend = BitacoraSeguimiento.objects.filter(estado='Pendiente').count()
            alertas_admin_count = vencen + pend

        total_badge = no_leidas if no_leidas > 0 else (alertas_admin_count if alertas_admin_count > 0 else 0)
        user_notif_data = {
            'recientes': recientes,
            'total_badge': total_badge,
            'tiene_alertas_admin': alertas_admin_count > 0,
        }
        cache.set(cache_key_user, user_notif_data, timeout=30)

    return {
        'notificaciones_campana': user_notif_data['recientes'],
        'num_notificaciones_no_leidas': user_notif_data['total_badge'],
        'tiene_alertas_admin': user_notif_data['tiene_alertas_admin'],
        'colegio': colegio,
        'tema_colores': tema_colores,
    }
