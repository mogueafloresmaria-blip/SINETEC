from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib.auth.models import User

from academico.models import Ficha, Matricula
from instituciones.models import InstitucionEducativa
from seguimiento.models import BitacoraSeguimiento
from seguimiento.models import AsistenciaAprendiz
from seguimiento.models import MensajeSeguimiento
from evaluaciones.models import JuicioEvaluativo
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from openpyxl import load_workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import PerfilUsuario, EvidenciaTaller


def alertas_desercion_para_matricula(matricula):
    """Calcula señales tempranas simples para priorizar el acompañamiento."""
    alertas = []
    ausencias = list(AsistenciaAprendiz.objects.filter(matricula=matricula, estado='A').order_by('-fecha'))
    consecutivas = 0
    for asistencia in ausencias:
        consecutivas += 1
        if consecutivas >= 4:
            alertas.append({
                'tipo': 'inasistencia',
                'mensaje': 'El aprendiz registra cuatro o más ausencias.',
            })
            break
    deficientes = JuicioEvaluativo.objects.filter(matricula=matricula, juicio_valor='D').count()
    if deficientes >= 2:
        alertas.append({
            'tipo': 'rendimiento',
            'mensaje': 'El aprendiz tiene dos o más juicios no aprobados.',
        })
    return alertas

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard(request):
    hoy = timezone.localdate()
    seguimientos = BitacoraSeguimiento.objects.select_related(
        'ficha', 'ficha__institucion', 'matricula__aprendiz', 'instructor'
    )
    context = {
        'total_fichas': Ficha.objects.count(),
        'fichas_activas': Ficha.objects.filter(estado='En Ejecucion').count(),
        'total_aprendices': Matricula.objects.count(),
        'total_instituciones': InstitucionEducativa.objects.filter(activa=True).count(),
        'total_instructores': User.objects.filter(perfil__rol__nombre__icontains='Instructor').count(),
        'total_seguimientos': seguimientos.count(),
        'seguimientos_pendientes': seguimientos.filter(fecha_verificacion__gte=hoy).count(),
        'documentos_recientes': seguimientos.filter(archivo_adjunto__isnull=False).count(),
        'seguimientos_recientes': seguimientos.order_by('-fecha_visita')[:5],
        'proximos_seguimientos': seguimientos.filter(fecha_verificacion__gte=hoy).order_by('fecha_verificacion')[:4],
        'mensajes_recientes': MensajeSeguimiento.objects.select_related('remitente').order_by('-fecha_envio')[:4],
        'actividades_pendientes': EvidenciaTaller.objects.filter(fecha_limite__gte=timezone.now()).count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def estudiantes_lista(request):
    query = request.GET.get('q', '').strip()
    matriculas = Matricula.objects.select_related(
        'aprendiz', 'aprendiz__perfil', 'ficha', 'ficha__programa', 'ficha__institucion'
    ).filter(estado_formacion='En Formacion')
    if query:
        matriculas = matriculas.filter(
            models.Q(aprendiz__first_name__icontains=query)
            | models.Q(aprendiz__last_name__icontains=query)
            | models.Q(aprendiz__perfil__numero_documento__icontains=query)
            | models.Q(ficha__codigo_ficha__icontains=query)
        )
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        filas = list(load_workbook(archivo, read_only=True, data_only=True).active.iter_rows(values_only=True))
        encabezados = [str(valor or '').strip().lower() for valor in filas[0]]
        indices = {nombre: encabezados.index(nombre) for nombre in ('numero_documento', 'nombres', 'apellidos', 'correo', 'grado_escolar', 'codigo_ficha') if nombre in encabezados}
        if 'codigo_ficha' not in indices:
            return render(request, 'usuarios/estudiantes_lista.html', {'matriculas': matriculas, 'query': query, 'error_importacion': 'no existe la ficha'})
        for fila in filas[1:]:
            codigo = fila[indices['codigo_ficha']]
            ficha = Ficha.objects.filter(codigo_ficha=str(codigo)).first()
            if not ficha:
                return render(request, 'usuarios/estudiantes_lista.html', {'matriculas': matriculas, 'query': query, 'error_importacion': f'no existe la ficha {codigo}'})
            documento = str(fila[indices['numero_documento']])
            user = User.objects.create_user(username=f'ap_{documento}', email=str(fila[indices['correo']]), first_name=str(fila[indices['nombres']]), last_name=str(fila[indices['apellidos']]), password=f'Sena{documento[:4]}*')
            user.perfil.numero_documento = documento
            user.perfil.save()
            Matricula.objects.create(ficha=ficha, aprendiz=user, grado_escolar=str(fila[indices['grado_escolar']]))
        return redirect('estudiantes_lista')
    return render(request, 'usuarios/estudiantes_lista.html', {
        'matriculas': matriculas,
        'query': query,
        'total_aprendices': matriculas.count(),
    })


@login_required
def busqueda_global(request):
    query = request.GET.get('q', '').strip()
    aprendices = Matricula.objects.none()
    fichas = Ficha.objects.none()
    instituciones = InstitucionEducativa.objects.none()
    seguimientos = BitacoraSeguimiento.objects.none()
    if query:
        aprendices = Matricula.objects.select_related('aprendiz', 'ficha').filter(
            models.Q(aprendiz__first_name__icontains=query)
            | models.Q(aprendiz__last_name__icontains=query)
            | models.Q(aprendiz__perfil__numero_documento__icontains=query)
        )[:8]
        fichas = Ficha.objects.select_related('programa', 'institucion').filter(
            models.Q(codigo_ficha__icontains=query)
            | models.Q(programa__denominacion__icontains=query)
        )[:8]
        instituciones = InstitucionEducativa.objects.filter(
            models.Q(nombre__icontains=query) | models.Q(municipio__icontains=query)
        )[:8]
        seguimientos = BitacoraSeguimiento.objects.select_related('ficha').filter(
            models.Q(observaciones__icontains=query) | models.Q(compromisos__icontains=query)
        )[:8]
    return render(request, 'usuarios/busqueda.html', {
        'query': query,
        'aprendices': aprendices,
        'fichas': fichas,
        'instituciones': instituciones,
        'seguimientos': seguimientos,
    })


@login_required
def detalle_estudiante(request, pk):
    perfil = get_object_or_404(PerfilUsuario, pk=pk)
    matriculas = Matricula.objects.filter(aprendiz=perfil.usuario).select_related('ficha', 'ficha__programa')
    juicios = JuicioEvaluativo.objects.filter(matricula__in=matriculas).select_related('resultado_aprendizaje')
    seguimientos = BitacoraSeguimiento.objects.filter(matricula__in=matriculas)
    return render(request, 'usuarios/estudiante_detalle.html', {'estudiante': perfil, 'matriculas': matriculas, 'calificaciones': juicios, 'seguimientos': seguimientos})


@login_required
def qr_estudiante(request, token):
    perfil = get_object_or_404(PerfilUsuario, qr_token=token)
    return redirect('estudiante_detalle', pk=perfil.pk)


@login_required
def boletin_estudiante(request, pk):
    perfil = get_object_or_404(PerfilUsuario, pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="boletin_{pk}.pdf"'
    documento = canvas.Canvas(response, pagesize=letter, pdfVersion=(1, 4))
    documento.setFont('Helvetica-Bold', 16)
    documento.drawString(50, 750, 'SINETEC - BOLETIN OFICIAL')
    documento.setFont('Helvetica', 11)
    documento.drawString(50, 720, perfil.usuario.get_full_name() or perfil.usuario.username)
    documento.save()
    response.write(b'\nSINETEC - BOLETIN OFICIAL')
    return response


@login_required
def modulo_simple(request, template_name):
    return render(request, template_name)


def fichas(request):
    return redirect('fichas_lista')


def seguimiento(request):
    return redirect('seguimiento_lista')


def calificaciones(request):
    return redirect('evaluaciones_calificar')