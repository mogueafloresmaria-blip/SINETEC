"""
Módulo de servicios avanzados de Asistencia Escolar y Detección Temprana para EDUNOVA.
Gestiona el cálculo de KPIs, historial individual, porcentajes ponderados oficiales
y alertas tempranas por ausencias consecutivas, tardanzas y justificaciones.
"""

from datetime import date, timedelta
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from seguimiento.models import AsistenciaAprendiz


def calcular_estadisticas_asistencia(matricula, fecha=None, fecha_hasta=None):
    """
    Calcula estadísticas acumuladas de asistencia para una matrícula escolar o grupo de matrículas.
    Fórmula coherente oficial:
    % Asistencia = (Presentes + [Tardanzas * 0.5] + Excusas) / Total Sesiones * 100
    - Presente: 100% de la sesión.
    - Tardanza: 50% de ponderación (asistió pero con retardo).
    - Excusa Justificada: 100% (falla justificada legalmente, no penaliza la asistencia).
    - Ausente injustificado: 0%.
    - Días sin registrar o fines de semana: NO se penalizan ni se cuentan como ausencias.
    """
    es_iterable = hasattr(matricula, '__iter__') and not hasattr(matricula, 'pk')
    if es_iterable:
        matriculas_lista = list(matricula)
        total_esperado = len(matriculas_lista)
        qs = AsistenciaAprendiz.objects.filter(matricula__in=matriculas_lista)
    else:
        total_esperado = 1
        qs = AsistenciaAprendiz.objects.filter(matricula=matricula)

    if fecha:
        qs = qs.filter(fecha=fecha)
    elif fecha_hasta:
        qs = qs.filter(fecha__lte=fecha_hasta)

    total = qs.count()
    p = qs.filter(estado='P').count()
    t = qs.filter(estado='T').count()
    a = qs.filter(estado='A').count()
    j = qs.filter(estado__in=['J', 'E']).count()
    pendientes = max(0, total_esperado - total) if fecha else 0

    if total == 0:
        return {
            'total': 0,
            'presentes': 0,
            'tardanzas': 0,
            'ausentes': 0,
            'excusas': 0,
            'pendientes': pendientes,
            'porcentaje': None,
            'formula_explicacion': 'Sin registros de asistencia suficientes para calcular porcentaje.',
        }

    pct = round(((p + (t * 0.5) + j) / total) * 100, 1)

    return {
        'total': total,
        'presentes': p,
        'tardanzas': t,
        'ausentes': a,
        'excusas': j,
        'pendientes': pendientes,
        'porcentaje': pct,
        'formula_explicacion': (
            f"Fórmula: (Presentes ({p}) + [Tardanzas ({t}) × 0.5] + Excusas ({j})) / "
            f"Total Sesiones Registradas ({total}) × 100 = {pct}%"
        ),
    }


def calcular_alertas_asistencia(matricula, fecha_referencia=None):
    """
    Analiza la base de datos real para emitir alertas objetivas de asistencia escolar:
    - 'No asistió hoy': Si la sesión de hoy está registrada como Ausente ('A').
    - 'Lleva 4 días consecutivos sin asistir': Cuatro días escolares consecutivos con inasistencia.
    - 'Lleva 5 días consecutivos sin asistir': Cinco o más días escolares consecutivos con inasistencia.
    - 'Tiene X ausencias justificadas': Si acumula 4 o más fallas justificadas.
    - 'Acumula varias tardanzas': Si acumula 3 o más tardanzas registradas.
    - 'Ha asistido regularmente': Si la asistencia es >= 90% y no tiene alertas críticas.
    - 'Ha venido siempre': 100% de asistencia (todas las sesiones registradas en 'P').
    - Regla de calendario: Fines de semana y días sin registro NO se consideran ausencias.
    """
    fecha_ref = fecha_referencia or timezone.localdate()
    stats = calcular_estadisticas_asistencia(matricula, fecha_hasta=fecha_ref)
    total = stats['total']

    if total == 0:
        return {
            'stats': stats,
            'alertas': [],
            'consecutivas': 0,
            'estado_resumen': 'Sin historial suficiente',
            'ha_venido_siempre': False,
        }

    asistencias_ordenadas = list(
        AsistenciaAprendiz.objects.filter(matricula=matricula, fecha__lte=fecha_ref)
        .order_by('-fecha')
    )

    # 1. Conteo de ausencias consecutivas hacia atrás en días registrados
    consecutivas = 0
    for asist in asistencias_ordenadas:
        # Fines de semana no lectivos se ignoran como ausencias
        if asist.fecha.weekday() >= 5:
            continue
        if asist.estado == 'A':
            consecutivas += 1
        else:
            # Una presencia, tardanza o excusa justificada rompe la racha de inasistencia consecutiva
            break

    alertas = []

    # 2. Alerta de ausencia hoy
    asist_hoy = next((a for a in asistencias_ordenadas if a.fecha == fecha_ref), None)
    if asist_hoy and asist_hoy.estado == 'A':
        alertas.append({
            'tipo': 'inasistencia_hoy',
            'nivel': 'danger',
            'titulo': 'Inasistencia Registrada Hoy',
            'mensaje': 'El estudiante no asistió hoy a la jornada académica.',
            'icono': 'bi-x-circle-fill'
        })

    # 3. Alertas por ausencias consecutivas
    if consecutivas == 4:
        alertas.append({
            'tipo': 'consecutivas_4',
            'nivel': 'danger',
            'titulo': 'Alerta de Inasistencia: 4 Días Consecutivos',
            'mensaje': 'Lleva 4 días consecutivos sin asistir a clases.',
            'icono': 'bi-exclamation-triangle-fill'
        })
    elif consecutivas >= 5:
        alertas.append({
            'tipo': 'consecutivas_5',
            'nivel': 'danger',
            'titulo': f'Alerta Crítica: {consecutivas} Días Consecutivos',
            'mensaje': f'Lleva {consecutivas} días consecutivos sin asistir a la institución.',
            'icono': 'bi-alarm-fill'
        })

    # 4. Alerta por acumulación de excusas justificadas
    if stats['excusas'] >= 4:
        alertas.append({
            'tipo': 'excusas_acumuladas',
            'nivel': 'info',
            'titulo': 'Excusas Justificadas Acumuladas',
            'mensaje': f'Tiene {stats["excusas"]} ausencias justificadas en el periodo.',
            'icono': 'bi-file-earmark-medical-fill'
        })

    # 5. Alerta por tardanzas acumuladas
    if stats['tardanzas'] >= 3:
        alertas.append({
            'tipo': 'tardanzas_acumuladas',
            'nivel': 'warning',
            'titulo': 'Tardanzas Reiteradas',
            'mensaje': f'Acumula varias tardanzas ({stats["tardanzas"]} registradas).',
            'icono': 'bi-clock-history'
        })

    # 6. Ha venido siempre o Asistencia Regular
    ha_venido_siempre = (
        total > 0 and
        stats['presentes'] == total and
        stats['ausentes'] == 0 and
        stats['tardanzas'] == 0
    )

    if ha_venido_siempre:
        alertas.append({
            'tipo': 'asistencia_perfecta',
            'nivel': 'success',
            'titulo': 'Asistencia Perfecta',
            'mensaje': 'Ha venido siempre. 100% de asistencia puntual a todas las clases registradas.',
            'icono': 'bi-patch-check-fill'
        })
        estado_resumen = 'Ha venido siempre'
    elif stats['porcentaje'] is not None and stats['porcentaje'] >= 90.0 and consecutivas < 2:
        alertas.append({
            'tipo': 'asistencia_regular',
            'nivel': 'success',
            'titulo': 'Asistencia Regular',
            'mensaje': f'Ha asistido regularmente ({stats["porcentaje"]}% de asistencia).',
            'icono': 'bi-check-circle-fill'
        })
        estado_resumen = 'Asistencia regular'
    elif consecutivas >= 4:
        estado_resumen = f'Riesgo: {consecutivas} días ausente'
    elif stats['ausentes'] > 0:
        estado_resumen = f'{stats["ausentes"]} ausencias acumuladas'
    else:
        estado_resumen = 'Asistencia en seguimiento'

    return {
        'stats': stats,
        'alertas': alertas,
        'consecutivas': consecutivas,
        'ausencias_consecutivas': consecutivas,
        'estado_resumen': estado_resumen,
        'ha_venido_siempre': ha_venido_siempre,
    }


def registrar_asistencia_estudiante(matricula, fecha, estado, registrado_por=None, docente=None, carga=None, periodo='Periodo 1', observaciones=''):
    """
    Guarda o actualiza la asistencia de UN estudiante de manera atómica y segura,
    sin borrar, alterar ni sobrescribir los registros de los demás estudiantes del grupo.
    """
    if estado not in ['P', 'T', 'A', 'J', 'E']:
        raise ValueError(f"Estado de asistencia inválido: {estado}")

    usuario_registrador = registrado_por or docente
    estado_normalizado = 'J' if estado == 'E' else estado

    with transaction.atomic():
        asist_obj, created = AsistenciaAprendiz.objects.update_or_create(
            matricula=matricula,
            fecha=fecha,
            defaults={
                'estado': estado_normalizado,
                'observaciones': observaciones,
                'registrado_por': usuario_registrador,
                'carga_academica': carga,
                'periodo': periodo,
            }
        )

    return asist_obj, created
