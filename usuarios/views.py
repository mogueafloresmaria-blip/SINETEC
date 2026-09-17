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
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from datetime import timedelta
from openpyxl import load_workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from .models import PerfilUsuario, EvidenciaTaller, CalificacionEvidencia, ResultadoAprendizaje, Rol


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
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html')

@login_required
def dashboard(request):
    hoy = timezone.localdate()
    seguimientos = BitacoraSeguimiento.objects.select_related(
        'ficha', 'ficha__institucion', 'matricula__aprendiz', 'instructor'
    )
    rol_usuario = getattr(getattr(request.user, 'perfil', None), 'rol', None)
    rol_nombre = rol_usuario.nombre if rol_usuario else 'Usuario'
    modulos_disponibles = [
        {'titulo': 'Fichas y programas', 'descripcion': 'Gestión de cohortes, horarios y rutas formativas.', 'icono': 'bi-layers', 'activo': True},
        {'titulo': 'Evaluación RAP', 'descripcion': 'Juicios, evidencias, seguimiento académico y retroalimentación.', 'icono': 'bi-award', 'activo': True},
        {'titulo': 'Control de asistencia', 'descripcion': 'Asistencias diarias, alertas y acompañamiento académico.', 'icono': 'bi-calendar2-check', 'activo': rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA']},
        {'titulo': 'Extranet / familias', 'descripcion': 'Acceso a horarios, seguimientos, materiales y comunicación.', 'icono': 'bi-people', 'activo': rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA', 'Estudiante']},
        {'titulo': 'Google Classroom', 'descripcion': 'Integración con actividades, contenidos y tareas externas.', 'icono': 'bi-google', 'activo': rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA']},
        {'titulo': 'Carnet QR', 'descripcion': 'Control de ingreso con renovación diaria y acceso a información.', 'icono': 'bi-qr-code-scan', 'activo': rol_nombre in ['Administrador', 'Coordinador', 'Estudiante']},
    ]
    tablero_fichas = []
    for ficha in Ficha.objects.select_related('programa', 'institucion', 'instructor_lider')[:6]:
        tablero_fichas.append({
            'codigo': ficha.codigo_ficha,
            'programa': ficha.programa.denominacion,
            'institucion': ficha.institucion.nombre,
            'instructor': ficha.instructor_lider.get_full_name() or ficha.instructor_lider.username,
            'jornada': 'Diurna',
            'estado': ficha.estado,
            'aprendices': Matricula.objects.filter(ficha=ficha).count(),
            'modulos': ['RAP', 'Asistencia', 'Documentos', 'Mensajería'],
        })
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
        'rol_usuario': rol_nombre,
        'modulos_disponibles': modulos_disponibles,
        'tablero_fichas': tablero_fichas,
    }
    return render(request, 'dashboard.html', context)


@login_required
def alertas_tempranas(request):
    """Centro operativo de alertas, actividades, documentos y rendimiento SENA."""
    hoy = timezone.localdate()
    limite = hoy + timedelta(days=7)
    matriculas = Matricula.objects.select_related(
        'aprendiz', 'aprendiz__perfil', 'ficha', 'ficha__programa', 'ficha__institucion'
    ).filter(estado_formacion='En Formacion')
    alertas = []
    for matricula in matriculas:
        motivos = alertas_desercion_para_matricula(matricula)
        if motivos:
            nivel = 'danger' if len(motivos) > 1 else 'warning'
            alertas.append({
                'matricula': matricula,
                'motivos': [{'detalle': motivo['mensaje']} for motivo in motivos],
                'nivel': nivel,
                'nivel_texto': 'Riesgo alto' if nivel == 'danger' else 'Atención requerida',
            })

    compromisos = BitacoraSeguimiento.objects.select_related(
        'ficha', 'matricula__aprendiz', 'instructor'
    ).filter(fecha_verificacion__isnull=False, fecha_verificacion__lte=limite).order_by('fecha_verificacion')
    fichas_por_finalizar = Ficha.objects.select_related('programa').filter(
        estado='En Ejecucion', fecha_fin__gte=hoy, fecha_fin__lte=hoy + timedelta(days=30)
    ).order_by('fecha_fin')
    actividades = EvidenciaTaller.objects.select_related('rap').prefetch_related('calificaciones').filter(
        fecha_limite__gte=timezone.now()
    ).order_by('fecha_limite')
    entregas_pendientes = CalificacionEvidencia.objects.select_related(
        'evidencia', 'aprendiz'
    ).filter(juicio_evaluativo='PENDIENTE').order_by('-fecha_entrega')
    seguimientos = BitacoraSeguimiento.objects.select_related(
        'ficha', 'matricula__aprendiz', 'instructor'
    ).order_by('-fecha_visita')
    documentos = [
        {'nombre': seguimiento.archivo_adjunto.name.rsplit('/', 1)[-1], 'url': seguimiento.archivo_adjunto.url,
         'tipo': 'Soporte de seguimiento', 'fecha': seguimiento.fecha_registro, 'ficha': seguimiento.ficha.codigo_ficha}
        for seguimiento in seguimientos if seguimiento.archivo_adjunto
    ][:10]
    documentos += [
        {'nombre': entrega.archivo_entregado.name.rsplit('/', 1)[-1], 'url': entrega.archivo_entregado.url,
         'tipo': 'Evidencia de aprendiz', 'fecha': entrega.fecha_entrega, 'ficha': entrega.evidencia.rap.codigo}
        for entrega in entregas_pendientes if entrega.archivo_entregado
    ][:10]
    juicios = JuicioEvaluativo.objects.select_related('resultado_aprendizaje').all()
    total_juicios = juicios.count()
    aprobados = juicios.filter(juicio_valor='A').count()
    no_aprobados = juicios.filter(juicio_valor='D').count()
    dificultad = list(juicios.filter(juicio_valor='D').values(
        'resultado_aprendizaje__codigo', 'resultado_aprendizaje__descripcion'
    ).annotate(total=models.Count('id')).order_by('-total')[:5])
    rol = getattr(getattr(request.user, 'perfil', None), 'rol', None)
    return render(request, 'usuarios/alertas_tempranas.html', {
        'alertas': alertas,
        'compromisos': compromisos[:8],
        'fichas_por_finalizar': fichas_por_finalizar[:8],
        'actividades': actividades[:8],
        'entregas_pendientes': entregas_pendientes[:8],
        'documentos': documentos[:12],
        'seguimientos_fotograficos': [s for s in seguimientos if s.archivo_adjunto and s.archivo_adjunto.name.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))][:8],
        'total_alertas': len(alertas),
        'total_urgentes': sum(a['nivel'] == 'danger' for a in alertas),
        'total_compromisos': compromisos.count(),
        'total_actividades': actividades.count(),
        'porcentaje_aprobados': round(aprobados * 100 / total_juicios) if total_juicios else 0,
        'porcentaje_no_aprobados': round(no_aprobados * 100 / total_juicios) if total_juicios else 0,
        'dificultad': dificultad,
        'rol_actual': rol.nombre if rol else 'Usuario SINETEC',
        'puede_gestionar': request.user.is_superuser or not rol or rol.nombre in {'Administrador', 'Coordinador', 'Instructor SENA'},
        'hoy': hoy,
    })


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
            rol_estudiante, _ = Rol.objects.get_or_create(
                nombre='Estudiante',
                defaults={'descripcion': 'Aprendiz SENA en formación'},
            )
            user.perfil.rol = rol_estudiante
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
def registrar_aprendiz(request):
    fichas = Ficha.objects.select_related('programa', 'institucion').filter(estado='En Ejecucion').order_by('codigo_ficha')
    return render(request, 'usuarios/registrar_aprendiz.html', {'fichas': fichas})


@login_required
def biblioteca_formacion(request):
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '').strip()
    fichas = Ficha.objects.select_related('programa').filter(estado='En Ejecucion')
    evidencias = EvidenciaTaller.objects.select_related('rap', 'rap__ficha').filter(
        fecha_limite__gte=timezone.now()
    ).order_by('fecha_limite')
    if query:
        fichas = fichas.filter(
            models.Q(codigo_ficha__icontains=query)
            | models.Q(programa__denominacion__icontains=query)
        )
        evidencias = evidencias.filter(
            models.Q(titulo__icontains=query)
            | models.Q(descripcion__icontains=query)
            | models.Q(rap__codigo__icontains=query)
        )
    if tipo == 'fichas':
        evidencias = evidencias.none()
    elif tipo == 'guias':
        fichas = fichas.none()
    return render(request, 'usuarios/biblioteca.html', {
        'fichas': fichas[:20],
        'evidencias': evidencias[:20],
        'query': query,
        'tipo': tipo,
        'total_fichas': fichas.count(),
        'total_guias': evidencias.count(),
    })


@login_required
def mensajeria(request):
    if request.method == 'POST':
        destinatario = request.POST.get('destinatario', '').strip()
        asunto = request.POST.get('asunto', 'Comunicación SINETEC').strip()
        contenido = request.POST.get('contenido', '').strip()
        if destinatario and contenido:
            send_mail(
                subject=asunto,
                message=f'{contenido}\n\nRemitente: {request.user.get_full_name() or request.user.username}',
                from_email=None,
                recipient_list=[destinatario] if '@' in destinatario else ['coordinacion@sena.edu.co'],
                fail_silently=True,
            )
            messages.success(request, 'La comunicación fue enviada al canal de coordinación.')
        else:
            messages.error(request, 'Indica un destinatario y escribe el mensaje antes de enviarlo.')
        return redirect('mensajeria')
    return render(request, 'mensajeria.html')


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
    if perfil.rol and perfil.rol.nombre == 'Estudiante' and perfil.qr_rotacion != timezone.localdate():
        perfil.save()
    matriculas = Matricula.objects.filter(aprendiz=perfil.usuario).select_related('ficha', 'ficha__programa')
    juicios = JuicioEvaluativo.objects.filter(matricula__in=matriculas).select_related('resultado_aprendizaje')
    seguimientos = BitacoraSeguimiento.objects.filter(matricula__in=matriculas)
    return render(request, 'usuarios/estudiante_detalle.html', {'estudiante': perfil, 'matriculas': matriculas, 'calificaciones': juicios, 'seguimientos': seguimientos})


@login_required
def qr_estudiante(request, token):
    perfil = get_object_or_404(PerfilUsuario, qr_token=token)
    if request.GET.get('dia') != str(timezone.localdate()) or perfil.qr_rotacion != timezone.localdate():
        return render(request, 'usuarios/qr_invalido.html', status=410)
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


@login_required
def fichas(request):
    return redirect('fichas_lista')


def seguimiento(request):
    return redirect('seguimiento_lista')


def calificaciones(request):
    return redirect('evaluaciones_calificar')


@login_required
def instructor_dashboard(request):
    evidencias = EvidenciaTaller.objects.select_related('rap', 'rap__ficha').prefetch_related('calificaciones').order_by('fecha_limite')
    entregas = CalificacionEvidencia.objects.select_related('evidencia', 'aprendiz').order_by('-fecha_entrega')
    return render(request, 'instructor.html', {
        'evidencias': evidencias,
        'entregas': entregas[:8],
        'total_evidencias': evidencias.count(),
        'total_entregas': entregas.count(),
        'pendientes_calificar': entregas.filter(juicio_evaluativo='PENDIENTE').count(),
        'raps': ResultadoAprendizaje.objects.all().order_by('codigo'),
    })


@login_required
def crear_evidencia(request):
    raps = ResultadoAprendizaje.objects.all().order_by('codigo')
    if request.method == 'POST':
        rap = get_object_or_404(raps, pk=request.POST.get('rap_id'))
        evidencia = EvidenciaTaller.objects.create(
            rap=rap,
            titulo=request.POST.get('titulo', '').strip(),
            descripcion=request.POST.get('descripcion', '').strip(),
            fecha_limite=request.POST.get('fecha_limite'),
        )
        messages.success(request, f'La evidencia “{evidencia.titulo}” fue publicada.')
        return redirect('instructor_dashboard')
    return render(request, 'usuarios/crear_evidencia.html', {'raps': raps})


@login_required
def entregar_evidencia(request, pk):
    evidencia = get_object_or_404(EvidenciaTaller.objects.select_related('rap'), pk=pk)
    if request.method == 'POST' and request.FILES.get('archivo_entregado'):
        CalificacionEvidencia.objects.update_or_create(
            evidencia=evidencia,
            aprendiz=request.user,
            defaults={'archivo_entregado': request.FILES['archivo_entregado'], 'juicio_evaluativo': 'PENDIENTE'},
        )
        messages.success(request, 'Tu evidencia fue entregada correctamente.')
        return redirect('aprendiz_dashboard')
    return render(request, 'usuarios/entregar_evidencia.html', {'evidencia': evidencia})


@login_required
def revisar_evidencia(request, pk):
    entrega = get_object_or_404(CalificacionEvidencia.objects.select_related('evidencia', 'aprendiz'), pk=pk)
    if request.method == 'POST':
        juicio = request.POST.get('juicio_evaluativo')
        if juicio in {'A', 'D'}:
            entrega.juicio_evaluativo = juicio
            entrega.observaciones = request.POST.get('observaciones', '').strip()
            entrega.save(update_fields=['juicio_evaluativo', 'observaciones'])
            messages.success(request, 'La retroalimentación fue guardada.')
            return redirect('instructor_dashboard')
    return render(request, 'usuarios/revisar_evidencia.html', {'entrega': entrega})


@login_required
def aprendiz_dashboard(request):
    entregas = CalificacionEvidencia.objects.filter(aprendiz=request.user).select_related('evidencia', 'evidencia__rap').order_by('-fecha_entrega')
    pendientes = EvidenciaTaller.objects.exclude(calificaciones__aprendiz=request.user).order_by('fecha_limite')
    return render(request, 'aprendiz.html', {'entregas': entregas, 'pendientes': pendientes})


@login_required
def coordinador_dashboard(request):
    fichas = Ficha.objects.select_related('programa', 'instructor_lider').order_by('-fecha_inicio')
    matriculas = Matricula.objects.filter(estado_formacion='En Formacion')
    seguimientos = BitacoraSeguimiento.objects.select_related('ficha', 'instructor').order_by('-fecha_visita')
    juicios = JuicioEvaluativo.objects.all()
    return render(request, 'coordinador.html', {
        'fichas': fichas[:8],
        'total_fichas': fichas.count(),
        'fichas_activas': fichas.filter(estado='En Ejecucion').count(),
        'total_aprendices': matriculas.count(),
        'seguimientos_pendientes': seguimientos.filter(fecha_verificacion__gte=timezone.localdate()).count(),
        'juicios_aprobados': juicios.filter(juicio_valor='A').count(),
        'juicios_por_mejorar': juicios.filter(juicio_valor='D').count(),
        'alertas_activas': sum(bool(alertas_desercion_para_matricula(m)) for m in matriculas.select_related('aprendiz')),
        'seguimientos_recientes': seguimientos[:6],
    })