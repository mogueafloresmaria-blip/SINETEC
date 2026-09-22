import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date
import csv
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from usuarios.decorators import requerir_roles
from usuarios.models import CalificacionEvidencia
from .models import JuicioEvaluativo
from academico.models import Ficha, ResultadoAprendizaje, Matricula, Competencia, SemaforoCompetencia
from seguimiento.models import RegistroAuditoria


TRIMESTRES = (
    ('1', 'Trimestre 1 (enero - marzo)'),
    ('2', 'Trimestre 2 (abril - junio)'),
    ('3', 'Trimestre 3 (julio - septiembre)'),
    ('4', 'Trimestre 4 (octubre - diciembre)'),
)


def filtrar_juicios_por_periodo(juicios, periodo_academico, trimestre):
    if periodo_academico:
        try:
            año = int(periodo_academico)
            juicios = juicios.filter(
                fecha_evaluacion__gte=date(año, 1, 1),
                fecha_evaluacion__lte=date(año, 12, 31),
            )
        except (TypeError, ValueError):
            pass

    if trimestre in {'1', '2', '3', '4'}:
        inicio_mes = (int(trimestre) - 1) * 3 + 1
        juicios = juicios.filter(
            fecha_evaluacion__month__gte=inicio_mes,
            fecha_evaluacion__month__lte=inicio_mes + 2,
        )
    return juicios


def periodos_para_ficha(ficha):
    if not ficha:
        return []
    inicio = ficha.fecha_inicio.year if ficha.fecha_inicio else timezone.now().year
    fin = ficha.fecha_fin.year if ficha.fecha_fin else inicio + 1
    return [str(año) for año in range(inicio, fin + 1)]


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Instructor SENA')
def sabana_calificaciones(request):
    """
    Sábana interactiva de evaluación masiva de Resultados de Aprendizaje (RAP).
    Permite al instructor seleccionar Ficha y RAP, y asentar juicios 'A' o 'D'
    para toda la lista de aprendices. Valida las reglas RN-003 y RN-004.
    """
    ficha_id = request.GET.get('ficha', None)
    rap_id = request.GET.get('rap', None)
    periodo_academico = request.GET.get('periodo', '').strip()
    trimestre = request.GET.get('trimestre', '').strip()
    juicio_filtro = request.GET.get('juicio', '').strip()

    fichas = Ficha.objects.all().order_by('codigo_ficha')
    ficha_actual = None
    rap_actual = None
    aprendices_datos = []
    total_aprendices = 0
    total_aprobados = 0
    total_deficientes = 0

    if ficha_id:
        ficha_actual = get_object_or_404(Ficha, pk=ficha_id)
        raps = ResultadoAprendizaje.objects.filter(competencia__programa=ficha_actual.programa).select_related('competencia')
    else:
        raps = ResultadoAprendizaje.objects.none()

    if ficha_actual and rap_id:
        rap_actual = get_object_or_404(
            raps,
            pk=rap_id,
        )

        if request.method == 'POST':
            if ficha_actual.periodo_cerrado:
                messages.error(request, "Acción Denegada (RN-004): El periodo de esta ficha se encuentra cerrado. No se pueden modificar calificaciones.")
                return redirect(f"/evaluaciones/?ficha={ficha_id}&rap={rap_id}")

            matriculas = ficha_actual.matriculas.select_related('aprendiz').all()
            guardados = 0

            for mat in matriculas:
                juicio_key = f"juicio_{mat.id}"
                obs_key = f"obs_{mat.id}"
                juicio_valor = request.POST.get(juicio_key, '').strip()
                observacion = request.POST.get(obs_key, '').strip()

                if juicio_valor in ['A', 'D']:
                    JuicioEvaluativo.objects.update_or_create(
                        matricula=mat,
                        resultado_aprendizaje=rap_actual,
                        defaults={
                            'instructor': request.user,
                            'juicio_valor': juicio_valor,
                            'observaciones': observacion,
                            'fecha_evaluacion': timezone.now().date(),
                        }
                    )
                    guardados += 1

            messages.success(request, f"Se asentaron exitosamente {guardados} juicios evaluativos para el resultado {rap_actual.codigo}.")
            return redirect(f"/evaluaciones/?ficha={ficha_id}&rap={rap_id}")

        matriculas = ficha_actual.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name')
        juicios = JuicioEvaluativo.objects.filter(
            matricula__in=matriculas,
            resultado_aprendizaje=rap_actual,
        )
        juicios = filtrar_juicios_por_periodo(juicios, periodo_academico, trimestre)
        if juicio_filtro in {'A', 'D'}:
            juicios = juicios.filter(juicio_valor=juicio_filtro)
        juicios_existentes = {
            j.matricula_id: j for j in JuicioEvaluativo.objects.filter(
                pk__in=juicios.values('pk')
            )
        }

        for mat in matriculas:
            juicio_obj = juicios_existentes.get(mat.id)
            aprendices_datos.append({
                'matricula': mat,
                'juicio_actual': juicio_obj.juicio_valor if juicio_obj else '',
                'observacion_actual': juicio_obj.observaciones if juicio_obj else '',
            })

        total_aprendices = len(aprendices_datos)
        total_aprobados = sum(item['juicio_actual'] == 'A' for item in aprendices_datos)
        total_deficientes = sum(item['juicio_actual'] == 'D' for item in aprendices_datos)
    porcentaje_aprobacion = round((total_aprobados / total_aprendices) * 100, 1) if total_aprendices else 0

    # Métricas reales de base de datos para los 4 cuadros superiores de la Sábana de Juicios
    if ficha_actual:
        juicios_scope = JuicioEvaluativo.objects.filter(matricula__ficha=ficha_actual)
        if rap_actual:
            juicios_scope = juicios_scope.filter(resultado_aprendizaje=rap_actual)
        total_evaluaciones = juicios_scope.count()
        total_aprobados_kpi = juicios_scope.filter(juicio_valor='A').count()
        total_deficientes_kpi = juicios_scope.filter(juicio_valor='D').count()
        
        matriculas_count = ficha_actual.matriculas.count()
        if rap_actual:
            total_pendientes = max(0, matriculas_count - (total_aprobados_kpi + total_deficientes_kpi))
        else:
            total_pendientes = CalificacionEvidencia.objects.filter(
                evidencia__ficha=ficha_actual, juicio_evaluativo='PENDIENTE'
            ).count()
    else:
        juicios_scope = JuicioEvaluativo.objects.all()
        total_evaluaciones = juicios_scope.count()
        total_aprobados_kpi = juicios_scope.filter(juicio_valor='A').count()
        total_deficientes_kpi = juicios_scope.filter(juicio_valor='D').count()
        total_pendientes = CalificacionEvidencia.objects.filter(juicio_evaluativo='PENDIENTE').count()
        
    tasa_aprobacion = round((total_aprobados_kpi / total_evaluaciones) * 100, 1) if total_evaluaciones else 0

    context = {
        'fichas': fichas,
        'ficha_actual': ficha_actual,
        'raps': raps,
        'rap_actual': rap_actual,
        'aprendices_datos': aprendices_datos,
        'total_aprendices': total_aprendices,
        'total_aprobados': total_aprobados,
        'total_deficientes': total_deficientes,
        'porcentaje_aprobacion': porcentaje_aprobacion,
        'total_evaluaciones': total_evaluaciones,
        'total_aprobados_kpi': total_aprobados_kpi,
        'total_deficientes_kpi': total_deficientes_kpi,
        'total_pendientes': total_pendientes,
        'tasa_aprobacion': tasa_aprobacion,
        'periodo_academico': periodo_academico,
        'trimestre': trimestre,
        'periodos_academicos': periodos_para_ficha(ficha_actual),
        'trimestres': TRIMESTRES,
        'hay_notas': bool(juicios_existentes) if ficha_actual and rap_actual else False,
        'juicio_filtro': juicio_filtro,
    }
    return render(request, 'evaluaciones/calificar.html', context)


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Instructor SENA')
def exportar_sabana_excel(request):
    ficha = get_object_or_404(Ficha, pk=request.GET.get('ficha'))
    rap = get_object_or_404(
        ResultadoAprendizaje.objects.filter(competencia__programa=ficha.programa),
        pk=request.GET.get('rap'),
    )
    periodo_academico = request.GET.get('periodo', '').strip()
    trimestre = request.GET.get('trimestre', '').strip()
    juicios = JuicioEvaluativo.objects.filter(
        matricula__ficha=ficha,
        resultado_aprendizaje=rap,
    ).select_related('matricula__aprendiz').order_by('matricula__aprendiz__last_name')
    juicios = filtrar_juicios_por_periodo(juicios, periodo_academico, trimestre)

    if not juicios.exists():
        messages.warning(request, 'No hay notas registradas para exportar con los filtros seleccionados.')
        return redirect(
            f'/evaluaciones/?ficha={ficha.pk}&rap={rap.pk}&periodo={periodo_academico}&trimestre={trimestre}'
        )

    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Sábana de Calificaciones'
    hoja.append(['Ficha', 'RAP', 'Código', 'Documento', 'Aprendiz', 'Juicio', 'Observaciones', 'Fecha de evaluación'])
    for juicio in juicios:
        aprendiz = juicio.matricula.aprendiz
        hoja.append([
            ficha.codigo_ficha,
            rap.codigo,
            rap.descripcion,
            aprendiz.perfil.numero_documento,
            aprendiz.get_full_name() or aprendiz.username,
            juicio.get_juicio_valor_display(),
            juicio.observaciones or '',
            juicio.fecha_evaluacion.strftime('%Y-%m-%d'),
        ])
    hoja.freeze_panes = 'A2'
    hoja.auto_filter.ref = hoja.dimensions
    for columna in hoja.columns:
        ancho = max(len(str(celda.value or '')) for celda in columna) + 2
        hoja.column_dimensions[columna[0].column_letter].width = min(ancho, 45)

    respuesta = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    respuesta['Content-Disposition'] = f'attachment; filename="sabana_{ficha.codigo_ficha}_{rap.codigo}.xlsx"'
    libro.save(respuesta)
    return respuesta


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Instructor SENA', 'Docente I.E.')
def exportar_sabana_csv(request):
    ficha = get_object_or_404(Ficha, pk=request.GET.get('ficha'))
    rap = get_object_or_404(ResultadoAprendizaje, pk=request.GET.get('rap'))
    juicios = JuicioEvaluativo.objects.filter(
        matricula__ficha=ficha, resultado_aprendizaje=rap
    ).select_related('matricula__aprendiz').order_by('matricula__aprendiz__last_name')
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8')
    respuesta['Content-Disposition'] = f'attachment; filename="sabana_{ficha.codigo_ficha}_{rap.codigo}.csv"'
    respuesta.write('\ufeff')
    escritor = csv.writer(respuesta)
    escritor.writerow(['Ficha', 'RAP', 'Documento', 'Aprendiz', 'Juicio', 'Observaciones', 'Fecha'])
    for juicio in juicios:
        aprendiz = juicio.matricula.aprendiz
        escritor.writerow([
            ficha.codigo_ficha,
            rap.codigo,
            aprendiz.perfil.numero_documento,
            aprendiz.get_full_name() or aprendiz.username,
            juicio.get_juicio_valor_display(),
            juicio.observaciones or '',
            juicio.fecha_evaluacion.isoformat(),
        ])
    return respuesta


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Instructor SENA', 'Docente I.E.')
def reporte_rap_pdf(request):
    """
    Genera un informe en PDF con la sábana de notas de un RAP específico.
    """
    ficha_id = request.GET.get('ficha')
    rap_id = request.GET.get('rap')
    periodo_academico = request.GET.get('periodo', '').strip()
    trimestre = request.GET.get('trimestre', '').strip()

    ficha = get_object_or_404(Ficha, pk=ficha_id)
    rap = get_object_or_404(
        ResultadoAprendizaje.objects.filter(competencia__programa=ficha.programa),
        pk=rap_id,
    )

    juicios = JuicioEvaluativo.objects.filter(
        matricula__ficha=ficha,
        resultado_aprendizaje=rap,
    ).select_related('matricula__aprendiz', 'matricula__aprendiz__perfil').order_by('matricula__aprendiz__last_name')

    juicios = filtrar_juicios_por_periodo(juicios, periodo_academico, trimestre)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Reporte_RAP_{rap.codigo}_Ficha_{ficha.codigo_ficha}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado institucional SINETEC
    p.setFillColor(colors.HexColor("#1E3A8A"))
    p.rect(0, height - 85, width, 85, fill=True, stroke=False)
    p.setFillColor(colors.HexColor("#0F2942"))
    p.rect(0, height - 90, width, 5, fill=True, stroke=False)

    # Logo SENA Oficial en el encabezado
    logo_sena_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'sena_logo_white.png')
    if os.path.exists(logo_sena_path):
        try:
            sena_img = ImageReader(logo_sena_path)
            p.drawImage(sena_img, width - 75, height - 72, width=54, height=54, mask='auto')
        except Exception:
            pass

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, height - 36, "SENA · SINETEC - REPORTE DE EVALUACIÓN DE RAP")

    p.setFont("Helvetica", 9)
    p.drawString(40, height - 55, f"Ficha: {ficha.codigo_ficha} | Programa: {ficha.programa.denominacion[:50]}")
    comp_desc = rap.competencia.descripcion[:65] if (rap.competencia and rap.competencia.descripcion) else 'Competencia Técnica'
    p.drawString(40, height - 70, f"RAP: {rap.codigo} - {rap.descripcion[:60]}")

    # Encabezados de la Tabla
    y = height - 125
    p.setFillColor(colors.HexColor("#0F172A"))
    p.rect(40, y - 5, width - 80, 22, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(48, y + 2, "No.")
    p.drawString(75, y + 2, "Documento")
    p.drawString(180, y + 2, "Apellidos y Nombres")
    p.drawString(380, y + 2, "Juicio Evaluativo")
    p.drawString(480, y + 2, "Observaciones")

    y -= 22
    p.setFont("Helvetica", 8.5)
    contador = 1

    for juicio in juicios:
        aprendiz = juicio.matricula.aprendiz
        doc = f"{aprendiz.perfil.tipo_documento} {aprendiz.perfil.numero_documento}" if hasattr(aprendiz, 'perfil') else "N/A"
        nombre = f"{aprendiz.last_name}, {aprendiz.first_name}"
        valor_juicio = "A - APROBADO" if juicio.juicio_valor == 'A' else ("D - POR MEJORAR" if juicio.juicio_valor == 'D' else "POR EVALUAR")
        obs = (juicio.observaciones[:24] + '...') if juicio.observaciones and len(juicio.observaciones) > 24 else (juicio.observaciones or '-')

        # Fondo alterno
        if contador % 2 == 0:
            p.setFillColor(colors.HexColor("#F8FAFC"))
            p.rect(40, y - 4, width - 80, 18, fill=True, stroke=False)

        p.setFillColor(colors.HexColor("#334155"))
        p.drawString(48, y, str(contador))
        p.drawString(75, y, doc)
        p.drawString(180, y, nombre[:34])

        if juicio.juicio_valor == 'A':
            p.setFillColor(colors.HexColor("#059669"))
            p.setFont("Helvetica-Bold", 8.5)
        else:
            p.setFillColor(colors.HexColor("#DC2626"))
            p.setFont("Helvetica-Bold", 8.5)
        p.drawString(380, y, valor_juicio)

        p.setFont("Helvetica", 8)
        p.setFillColor(colors.HexColor("#64748B"))
        p.drawString(480, y, obs)

        y -= 18
        contador += 1

        if y < 65:
            p.setFont("Helvetica-Oblique", 7.5)
            p.setFillColor(colors.HexColor("#94A3B8"))
            p.drawString(40, 30, "Documento de evaluación emitido por la plataforma SINETEC · Articulación con la Media Técnica SENA")
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 8.5)

    p.setFont("Helvetica-Oblique", 7.5)
    p.setFillColor(colors.HexColor("#94A3B8"))
    p.drawString(40, 30, "Documento de evaluación emitido por la plataforma SINETEC · Articulación con la Media Técnica SENA")

    p.showPage()
    p.save()
    return response


@login_required
def raps_por_ficha(request):
    ficha_id = request.GET.get('ficha_id')
    if not ficha_id:
        return JsonResponse({'raps': []})

    ficha = get_object_or_404(Ficha, pk=ficha_id)
    raps = ResultadoAprendizaje.objects.filter(
        competencia__programa=ficha.programa
    ).select_related('competencia').order_by('competencia__codigo', 'codigo')

    return JsonResponse({
        'raps': [
            {
                'id': rap.id,
                'codigo': rap.codigo,
                'descripcion': rap.descripcion,
                'competencia': rap.competencia.codigo,
            }
            for rap in raps
        ]
    })


@login_required
def aprendices_por_rap(request):
    ficha = get_object_or_404(Ficha, pk=request.GET.get('ficha_id'))
    rap = get_object_or_404(
        ResultadoAprendizaje.objects.filter(competencia__programa=ficha.programa),
        pk=request.GET.get('rap_id'),
    )
    juicios = JuicioEvaluativo.objects.filter(
        matricula__ficha=ficha,
        resultado_aprendizaje=rap,
    )
    juicios = filtrar_juicios_por_periodo(
        juicios,
        request.GET.get('periodo', '').strip(),
        request.GET.get('trimestre', '').strip(),
    )
    juicio_filtro = request.GET.get('juicio', '').strip()
    if juicio_filtro in {'A', 'D'}:
        juicios = juicios.filter(juicio_valor=juicio_filtro)
    juicios_por_matricula = {
        juicio.matricula_id: juicio
        for juicio in juicios
    }
    matriculas = ficha.matriculas.select_related(
        'aprendiz', 'aprendiz__perfil'
    ).order_by('aprendiz__last_name', 'aprendiz__first_name')
    aprendices = []
    for matricula in matriculas:
        juicio = juicios_por_matricula.get(matricula.pk)
        aprendices.append({
            'matricula_id': matricula.pk,
            'nombre': matricula.aprendiz.get_full_name() or matricula.aprendiz.username,
            'tipo_documento': matricula.aprendiz.perfil.tipo_documento,
            'numero_documento': matricula.aprendiz.perfil.numero_documento,
            'juicio': juicio.juicio_valor if juicio else '',
            'observacion': juicio.observaciones if juicio else '',
        })
    return JsonResponse({
        'ficha': {'id': ficha.pk, 'codigo': ficha.codigo_ficha},
        'rap': {'id': rap.pk, 'codigo': rap.codigo, 'descripcion': rap.descripcion},
        'periodo_cerrado': ficha.periodo_cerrado,
        'aprendices': aprendices,
    })


@login_required
@requerir_roles('Administrador', 'Coordinador')
def cerrar_periodo_ficha(request, ficha_id):
    """
    Cierre formal del periodo evaluativo de una ficha (RN-004).
    Solo para coordinadores o administradores.
    """
    ficha = get_object_or_404(Ficha, pk=ficha_id)
    if request.method == 'POST':
        ficha.periodo_cerrado = not ficha.periodo_cerrado
        ficha.save()
        estado_texto = "CERRADO" if ficha.periodo_cerrado else "REABIERTO"
        messages.info(request, f"El periodo evaluativo de la Ficha {ficha.codigo_ficha} ahora se encuentra {estado_texto}.")
        return redirect('fichas_detalle', pk=ficha.pk)

    return redirect('fichas_detalle', pk=ficha.pk)


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Instructor SENA', 'Docente I.E.', 'Estudiante', 'Aprendiz')
def semaforo_competencias(request):
    """
    Panel interactivo del Semáforo de Competencias con los 3 colores oficiales:
    🟢 Aprobado (APROBADO)
    🟡 En proceso (EN_PROCESO)
    🔴 Por recuperar (RECUPERAR)

    Permite al profesor calificar en 1 clic mediante API reactiva o guardado masivo,
    filtrar por color de semáforo, consultar estadísticas de avance y exportar el informe.
    """
    ficha_id = request.GET.get('ficha', '').strip()
    competencia_id = request.GET.get('competencia', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    query = request.GET.get('q', '').strip()

    es_estudiante = hasattr(request.user, 'perfil') and request.user.perfil.rol and request.user.perfil.rol.nombre in ['Estudiante', 'Aprendiz']

    fichas = Ficha.objects.all().select_related('programa', 'institucion').order_by('codigo_ficha')
    if es_estudiante:
        fichas = fichas.filter(matriculas__aprendiz=request.user)

    ficha_actual = None
    if ficha_id:
        ficha_actual = get_object_or_404(fichas, pk=ficha_id)
    elif fichas.exists():
        ficha_actual = fichas.first()

    competencias = Competencia.objects.none()
    competencia_actual = None

    if ficha_actual:
        competencias = Competencia.objects.filter(programa=ficha_actual.programa).order_by('codigo')
        if competencia_id:
            competencia_actual = competencias.filter(pk=competencia_id).first()
        if not competencia_actual and competencias.exists():
            competencia_actual = competencias.first()

    if request.method == 'POST' and request.POST.get('accion') == 'guardar_masivo':
        if es_estudiante:
            messages.error(request, "Los estudiantes solo tienen permiso de consulta en el Semáforo de Competencias.")
            return redirect(f"/evaluaciones/semaforo/?ficha={ficha_actual.id if ficha_actual else ''}&competencia={competencia_actual.id if competencia_actual else ''}")

        if ficha_actual and ficha_actual.periodo_cerrado:
            messages.error(request, "Acción denegada: El periodo evaluativo de esta ficha se encuentra cerrado.")
            return redirect(f"/evaluaciones/semaforo/?ficha={ficha_actual.id}&competencia={competencia_actual.id if competencia_actual else ''}")

        actualizados = 0
        matriculas_post = ficha_actual.matriculas.select_related('aprendiz').all() if ficha_actual else []
        for mat in matriculas_post:
            campo_estado = f"estado_{mat.id}"
            campo_obs = f"obs_{mat.id}"
            nuevo_estado = request.POST.get(campo_estado, '').strip()
            nueva_obs = request.POST.get(campo_obs, '').strip()

            if nuevo_estado in ['APROBADO', 'EN_PROCESO', 'RECUPERAR'] and competencia_actual:
                SemaforoCompetencia.objects.update_or_create(
                    matricula=mat,
                    competencia=competencia_actual,
                    defaults={
                        'profesor': request.user,
                        'estado': nuevo_estado,
                        'observaciones': nueva_obs,
                    }
                )
                actualizados += 1

        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Semáforo de Competencias',
            accion='Calificación Masiva de Competencias',
            detalles=f"Se actualizaron {actualizados} registros del Semáforo para la competencia {competencia_actual.codigo} en ficha {ficha_actual.codigo_ficha}.",
            request=request
        )
        messages.success(request, f"¡Éxito! Se actualizaron {actualizados} calificaciones en el Semáforo de Competencias.")
        return redirect(f"/evaluaciones/semaforo/?ficha={ficha_actual.id}&competencia={competencia_actual.id if competencia_actual else ''}")

    aprendices_datos = []
    total_evaluados = 0
    total_aprobados = 0
    total_en_proceso = 0
    total_recuperar = 0

    if ficha_actual and competencia_actual:
        matriculas_qs = ficha_actual.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name', 'aprendiz__first_name')
        if es_estudiante:
            matriculas_qs = matriculas_qs.filter(aprendiz=request.user)

        if query:
            matriculas_qs = matriculas_qs.filter(
                Q(aprendiz__first_name__icontains=query) |
                Q(aprendiz__last_name__icontains=query) |
                Q(aprendiz__username__icontains=query) |
                Q(aprendiz__perfil__numero_documento__icontains=query)
            )

        semaforos_dict = {
            s.matricula_id: s
            for s in SemaforoCompetencia.objects.filter(
                matricula__in=matriculas_qs,
                competencia=competencia_actual
            ).select_related('profesor')
        }

        for mat in matriculas_qs:
            sem_obj = semaforos_dict.get(mat.id)
            estado_actual = sem_obj.estado if sem_obj else 'EN_PROCESO'
            obs_actual = sem_obj.observaciones if sem_obj else ''

            if estado_filtro and estado_actual != estado_filtro:
                continue

            aprendices_datos.append({
                'matricula': mat,
                'semaforo': sem_obj,
                'estado_actual': estado_actual,
                'observacion_actual': obs_actual,
                'fecha_actualizacion': sem_obj.fecha_actualizacion if sem_obj else None,
                'profesor': sem_obj.profesor if sem_obj else None,
            })

            total_evaluados += 1
            if estado_actual == 'APROBADO':
                total_aprobados += 1
            elif estado_actual == 'EN_PROCESO':
                total_en_proceso += 1
            elif estado_actual == 'RECUPERAR':
                total_recuperar += 1

    pct_aprobados = round((total_aprobados / total_evaluados) * 100, 1) if total_evaluados else 0
    pct_en_proceso = round((total_en_proceso / total_evaluados) * 100, 1) if total_evaluados else 0
    pct_recuperar = round((total_recuperar / total_evaluados) * 100, 1) if total_evaluados else 0

    context = {
        'fichas': fichas,
        'ficha_actual': ficha_actual,
        'competencias': competencias,
        'competencia_actual': competencia_actual,
        'aprendices_datos': aprendices_datos,
        'total_evaluados': total_evaluados,
        'total_aprobados': total_aprobados,
        'total_en_proceso': total_en_proceso,
        'total_recuperar': total_recuperar,
        'pct_aprobados': pct_aprobados,
        'pct_en_proceso': pct_en_proceso,
        'pct_recuperar': pct_recuperar,
        'estado_filtro': estado_filtro,
        'query': query,
        'es_estudiante': es_estudiante,
    }
    return render(request, 'evaluaciones/semaforo.html', context)


@login_required
def api_actualizar_semaforo(request):
    """
    Endpoint AJAX para actualización instantánea en 1 clic del Semáforo de Competencia.
    Recibe: matricula_id, competencia_id, estado ('APROBADO', 'EN_PROCESO', 'RECUPERAR'), observaciones.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    if hasattr(request.user, 'perfil') and request.user.perfil.rol and request.user.perfil.rol.nombre in ['Estudiante', 'Aprendiz']:
        return JsonResponse({'status': 'error', 'message': 'Acceso no autorizado para estudiantes'}, status=403)

    if request.content_type == 'application/json':
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
            matricula_id = data.get('matricula_id')
            competencia_id = data.get('competencia_id')
            nuevo_estado = (data.get('estado') or '').strip()
            observaciones = (data.get('observaciones') or '').strip()
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'JSON payload inválido'}, status=400)
    else:
        matricula_id = request.POST.get('matricula_id')
        competencia_id = request.POST.get('competencia_id')
        nuevo_estado = request.POST.get('estado', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()

    if not matricula_id or not competencia_id or nuevo_estado not in ['APROBADO', 'EN_PROCESO', 'RECUPERAR']:
        return JsonResponse({'status': 'error', 'message': 'Datos incompletos o estado inválido'}, status=400)

    matricula = get_object_or_404(Matricula, pk=matricula_id)
    competencia = get_object_or_404(Competencia, pk=competencia_id)

    if matricula.ficha.periodo_cerrado:
        return JsonResponse({'status': 'error', 'message': 'El periodo de esta ficha está cerrado'}, status=400)

    semaforo, created = SemaforoCompetencia.objects.update_or_create(
        matricula=matricula,
        competencia=competencia,
        defaults={
            'profesor': request.user,
            'estado': nuevo_estado,
            'observaciones': observaciones,
        }
    )

    badge_map = {
        'APROBADO': ('bg-success text-white', '🟢 Aprobado', '🟢'),
        'EN_PROCESO': ('bg-warning text-dark', '🟡 En proceso', '🟡'),
        'RECUPERAR': ('bg-danger text-white', '🔴 Por recuperar', '🔴'),
    }
    badge_class, texto_estado, icono = badge_map[nuevo_estado]

    RegistroAuditoria.registrar(
        usuario=request.user,
        modulo='Semáforo de Competencias',
        accion='Actualización de Estado',
        detalles=f"Se actualizó a '{nuevo_estado}' la competencia {competencia.codigo} del estudiante {matricula.aprendiz.get_full_name()}.",
        request=request
    )

    return JsonResponse({
        'status': 'success',
        'nuevo_estado': nuevo_estado,
        'badge_class': badge_class,
        'texto_estado': texto_estado,
        'icono': icono,
        'aprendiz': matricula.aprendiz.get_full_name(),
        'actualizado_por': request.user.get_full_name() or request.user.username,
        'fecha': timezone.now().strftime('%d/%m/%Y %H:%M')
    })


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Instructor SENA', 'Docente I.E.')
def exportar_semaforo_excel(request):
    """
    Exporta la matriz de Semáforo de Competencias a un libro Excel (.xlsx).
    """
    ficha_id = request.GET.get('ficha')
    competencia_id = request.GET.get('competencia')
    estado_filtro = request.GET.get('estado', '').strip()

    if ficha_id:
        ficha = get_object_or_404(Ficha, pk=ficha_id)
    else:
        ficha = Ficha.objects.filter(matriculas__isnull=False).distinct().first() or Ficha.objects.first()

    if not ficha:
        messages.error(request, "No hay fichas registradas para exportar.")
        return redirect('semaforo_competencias')

    if competencia_id:
        competencia = get_object_or_404(Competencia, pk=competencia_id)
    else:
        competencia = (ficha.programa.competencias.first() if ficha.programa else None) or Competencia.objects.first()

    if not competencia:
        messages.error(request, "No hay competencias registradas para esta ficha.")
        return redirect('semaforo_competencias')

    matriculas = ficha.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name', 'aprendiz__first_name')
    semaforos = {
        s.matricula_id: s
        for s in SemaforoCompetencia.objects.filter(matricula__in=matriculas, competencia=competencia)
    }

    wb = Workbook()
    ws = wb.active
    ws.title = "Semáforo Competencias"

    ws.append(["SINETEC · SISTEMA ADMINISTRATIVO DE MEDIA TÉCNICA SENA"])
    ws.append([f"Ficha: {ficha.codigo_ficha} - {ficha.programa.denominacion}"])
    ws.append([f"Colegio: {ficha.institucion.nombre} | Municipio: {ficha.institucion.municipio}"])
    ws.append([f"Competencia: {competencia.codigo} - {competencia.descripcion[:80]}"])
    ws.append([])

    ws.append(["No.", "Tipo Doc", "Documento", "Apellidos y Nombres", "Semáforo", "Estado", "Observaciones / Plan de Mejora", "Última Actualización"])

    contador = 1
    for mat in matriculas:
        sem = semaforos.get(mat.id)
        estado = sem.estado if sem else 'EN_PROCESO'
        if estado_filtro and estado != estado_filtro:
            continue

        emoji = '🟢' if estado == 'APROBADO' else ('🟡' if estado == 'EN_PROCESO' else '🔴')
        texto = 'Aprobado' if estado == 'APROBADO' else ('En proceso' if estado == 'EN_PROCESO' else 'Por recuperar')
        obs = sem.observaciones if sem else ''
        f_act = sem.fecha_actualizacion.strftime('%Y-%m-%d %H:%M') if (sem and sem.fecha_actualizacion) else 'Pendiente'

        ws.append([
            contador,
            mat.aprendiz.perfil.tipo_documento if hasattr(mat.aprendiz, 'perfil') else "CC",
            mat.aprendiz.perfil.numero_documento if hasattr(mat.aprendiz, 'perfil') else "-",
            mat.aprendiz.get_full_name() or mat.aprendiz.username,
            emoji,
            texto,
            obs,
            f_act
        ])
        contador += 1

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 12), 40)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Semaforo_{ficha.codigo_ficha}_{competencia.codigo}.xlsx"'
    wb.save(response)
    return response


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Instructor SENA', 'Docente I.E.')
def exportar_semaforo_pdf(request):
    """
    Genera un informe oficial en PDF del Semáforo de Competencias con los 3 colores.
    """
    ficha_id = request.GET.get('ficha')
    competencia_id = request.GET.get('competencia')
    estado_filtro = request.GET.get('estado', '').strip()

    if ficha_id:
        ficha = get_object_or_404(Ficha, pk=ficha_id)
    else:
        ficha = Ficha.objects.filter(matriculas__isnull=False).distinct().first() or Ficha.objects.first()

    if not ficha:
        messages.error(request, "No hay fichas registradas para exportar.")
        return redirect('semaforo_competencias')

    if competencia_id:
        competencia = get_object_or_404(Competencia, pk=competencia_id)
    else:
        competencia = (ficha.programa.competencias.first() if ficha.programa else None) or Competencia.objects.first()

    if not competencia:
        messages.error(request, "No hay competencias registradas para esta ficha.")
        return redirect('semaforo_competencias')

    matriculas = ficha.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name', 'aprendiz__first_name')
    semaforos = {
        s.matricula_id: s
        for s in SemaforoCompetencia.objects.filter(matricula__in=matriculas, competencia=competencia)
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Semaforo_{ficha.codigo_ficha}_{competencia.codigo}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFillColor(colors.HexColor("#1E3A8A"))
    p.rect(0, height - 85, width, 85, fill=True, stroke=False)
    p.setFillColor(colors.HexColor("#0F2942"))
    p.rect(0, height - 90, width, 5, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, height - 34, "SINETEC - SEMÁFORO DE COMPETENCIAS ESCOLAR")

    p.setFont("Helvetica", 9)
    p.drawString(40, height - 52, f"Ficha: {ficha.codigo_ficha} | {ficha.programa.denominacion[:45]} | I.E.: {ficha.institucion.nombre[:40]}")
    p.drawString(40, height - 68, f"Norma / Competencia: {competencia.codigo} - {competencia.descripcion[:65]}")

    y = height - 120
    p.setFillColor(colors.HexColor("#0F172A"))
    p.rect(40, y - 5, width - 80, 22, fill=True, stroke=False)

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 8.5)
    p.drawString(48, y + 2, "No.")
    p.drawString(75, y + 2, "Documento")
    p.drawString(170, y + 2, "Apellidos y Nombres")
    p.drawString(365, y + 2, "Semáforo")
    p.drawString(460, y + 2, "Observaciones / Plan de Mejora")

    y -= 22
    p.setFont("Helvetica", 8)
    contador = 1

    for mat in matriculas:
        sem = semaforos.get(mat.id)
        estado = sem.estado if sem else 'EN_PROCESO'
        if estado_filtro and estado != estado_filtro:
            continue

        doc = f"{mat.aprendiz.perfil.tipo_documento} {mat.aprendiz.perfil.numero_documento}" if hasattr(mat.aprendiz, 'perfil') else "-"
        nombre = mat.aprendiz.get_full_name() or mat.aprendiz.username
        texto_estado = "APROBADO" if estado == 'APROBADO' else ("EN PROCESO" if estado == 'EN_PROCESO' else "POR RECUPERAR")
        color_hex = "#059669" if estado == 'APROBADO' else ("#D97706" if estado == 'EN_PROCESO' else "#DC2626")
        obs = (sem.observaciones[:28] + '...') if sem and sem.observaciones and len(sem.observaciones) > 28 else ((sem.observaciones if sem else '-') or '-')

        if contador % 2 == 0:
            p.setFillColor(colors.HexColor("#F8FAFC"))
            p.rect(40, y - 4, width - 80, 18, fill=True, stroke=False)

        p.setFillColor(colors.HexColor("#334155"))
        p.drawString(48, y, str(contador))
        p.drawString(75, y, doc)
        p.drawString(170, y, nombre[:32])

        p.setFillColor(colors.HexColor(color_hex))
        p.setFont("Helvetica-Bold", 8)
        p.drawString(365, y, texto_estado)

        p.setFont("Helvetica", 7.5)
        p.setFillColor(colors.HexColor("#64748B"))
        p.drawString(460, y, obs)

        y -= 18
        contador += 1

        if y < 60:
            p.setFont("Helvetica-Oblique", 7)
            p.setFillColor(colors.HexColor("#94A3B8"))
            p.drawString(40, 30, "Reporte oficial emitido por la plataforma SINETEC · Semáforo de Competencias Media Técnica SENA")
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 8)

    p.setFont("Helvetica-Oblique", 7)
    p.setFillColor(colors.HexColor("#94A3B8"))
    p.drawString(40, 30, "Reporte oficial emitido por la plataforma SINETEC · Semáforo de Competencias Media Técnica SENA")
    p.showPage()
    p.save()
    return response