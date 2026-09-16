from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import date
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from usuarios.decorators import requerir_roles
from .models import JuicioEvaluativo
from academico.models import Ficha, ResultadoAprendizaje, Matricula


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
    return [str(año) for año in range(ficha.fecha_inicio.year, ficha.fecha_fin.year + 1)]


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
    response['Content-Disposition'] = f'inline; filename="Reporte_RAP_{ficha.codigo_ficha}_{rap.codigo}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado con estética SINETEC (Rosa Pastel)
    p.setFillColorHex("#F8CEEC")
    p.rect(0, height - 90, width, 90, fill=True, stroke=False)

    p.setFillColorHex("#4A2E35")
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, height - 40, "SINETEC - INFORME EVALUATIVO DE APRENDIZAJE")

    p.setFont("Helvetica", 10)
    p.drawString(40, height - 65, f"Ficha: {ficha.codigo_ficha} | Programa: {ficha.programa.denominacion}")
    p.drawString(40, height - 80, f"RAP: {rap.codigo} - {rap.descripcion[:60]}")

    # Encabezados de la Tabla
    y = height - 130
    p.setFillColorHex("#4A2E35")
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "No.")
    p.drawString(70, y, "Documento")
    p.drawString(180, y, "Aprendiz")
    p.drawString(380, y, "Juicio Evaluativo")
    p.drawString(480, y, "Observaciones")

    p.setStrokeColorHex("#F8CEEC")
    p.setLineWidth(1)
    p.line(40, y - 5, width - 40, y - 5)

    y -= 25
    p.setFont("Helvetica", 9)
    contador = 1

    for juicio in juicios:
        aprendiz = juicio.matricula.aprendiz
        doc = f"{aprendiz.perfil.tipo_documento} {aprendiz.perfil.numero_documento}" if hasattr(aprendiz, 'perfil') else "N/A"
        nombre = f"{aprendiz.last_name}, {aprendiz.first_name}"
        valor_juicio = juicio.get_juicio_valor_display()
        obs = (juicio.observaciones[:20] + '...') if juicio.observaciones and len(juicio.observaciones) > 20 else (juicio.observaciones or '-')

        p.setFillColorHex("#333333")
        p.drawString(40, y, str(contador))
        p.drawString(70, y, doc)
        p.drawString(180, y, nombre[:30])

        if juicio.juicio_valor == 'A':
            p.setFillColorHex("#2E7D32")
        else:
            p.setFillColorHex("#C62828")
        p.drawString(380, y, valor_juicio)

        p.setFillColorHex("#666666")
        p.drawString(480, y, obs)

        y -= 20
        contador += 1

        if y < 60:
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 9)

    p.setFont("Helvetica-Oblique", 8)
    p.setFillColorHex("#888888")
    p.drawString(40, 30, "Documento generado por la plataforma SINETEC.")

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