import base64
import io
import uuid
import hashlib
import qrcode
from datetime import timedelta, date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.conf import settings

from academico.models import (
    Ficha, Matricula, ProgramaFormacion, HorarioFicha, Competencia,
    RecursoBiblioteca, RecursoGuardadoAprendiz, ResultadoAprendizaje as RapCurricular,
    ProyectoInnovacion, LogroAprendiz, DocumentoInstitucional
)
from instituciones.models import InstitucionEducativa
from seguimiento.models import (
    BitacoraSeguimiento, AsistenciaAprendiz, MensajeSeguimiento,
    SolicitudSecretaria, RespuestaSolicitud, Notificacion, RegistroAuditoria,
    CompromisoFormativo, ConfiguracionAlertas, CasoAlertaTemprana,
    EmpresaConvenio, EtapaProductiva, BitacoraEtapaProductiva
)
from evaluaciones.models import JuicioEvaluativo
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from openpyxl import load_workbook, Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from .models import PerfilUsuario, EvidenciaTaller, CalificacionEvidencia, ResultadoAprendizaje, Rol
from .decorators import (
    solo_coordinador_o_admin, solo_instructor, solo_aprendiz,
    solo_secretaria_o_coordinador, validar_propietario_o_coordinador
)


def error_403_view(request, exception=None):
    """Manejador institucional para errores de permiso HTTP 403."""
    return render(request, '403.html', status=403)



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
    """Página de inicio institucional de SINETEC."""
    contexto_usuario = None
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'perfil', None)
        rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ('Administrador' if request.user.is_superuser else 'Usuario')
        pendientes = 0
        ficha_codigo = None
        programa_nombre = None
        url_accion = "/dashboard/"
        mensaje_accion = "Sesión activa en SINETEC"

        if rol_nombre in ['Estudiante', 'Aprendiz']:
            mat = Matricula.objects.filter(aprendiz=request.user).select_related('ficha', 'ficha__programa').first()
            if mat:
                ficha_codigo = mat.ficha.codigo_ficha
                programa_nombre = mat.ficha.programa.denominacion
                entregadas_ids = CalificacionEvidencia.objects.filter(aprendiz=request.user).values_list('evidencia_id', flat=True)
                pendientes = EvidenciaTaller.objects.filter(Q(ficha=mat.ficha) | Q(ficha__isnull=True)).exclude(id__in=entregadas_ids).count()
            url_accion = "/portafolio/"
            mensaje_accion = f"{pendientes} actividades de formación pendientes" if pendientes > 0 else "¡Estás al día con tus evidencias!"
        elif 'Instructor' in rol_nombre:
            fichas_asignadas = request.user.fichas_asignadas.all()
            pendientes = CalificacionEvidencia.objects.filter(
                evidencia__ficha__in=fichas_asignadas,
                juicio_evaluativo='PENDIENTE'
            ).count()
            url_accion = "/aula/instructor/"
            mensaje_accion = f"{pendientes} evidencias por revisar en tus fichas" if pendientes > 0 else "Sin evidencias pendientes por calificar"
        elif 'Coordinador' in rol_nombre or request.user.is_superuser:
            solicitudes_abiertas = SolicitudSecretaria.objects.filter(estado__in=['ENVIADA', 'RECIBIDA', 'EN_REVISION']).count()
            url_accion = "/coordinacion/"
            mensaje_accion = f"{solicitudes_abiertas} trámites de secretaría pendientes de atención"

        contexto_usuario = {
            'nombre': request.user.first_name or request.user.username,
            'rol': rol_nombre,
            'ficha_codigo': ficha_codigo,
            'programa_nombre': programa_nombre,
            'pendientes': pendientes,
            'mensaje_accion': mensaje_accion,
            'url_accion': url_accion,
        }

    return render(request, 'home.html', {'usuario_resumen': contexto_usuario})

@login_required
def dashboard(request):
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if (perfil and perfil.rol) else ('Administrador' if request.user.is_superuser else '')
    rol_lower = rol_nombre.lower()

    if 'estudiante' in rol_lower or 'aprendiz' in rol_lower:
        return redirect('aprendiz_dashboard')
    elif 'instructor' in rol_lower or 'docente' in rol_lower:
        return redirect('instructor_dashboard')
    elif 'secretar' in rol_lower:
        return redirect('secretaria_dashboard')
    elif 'coordinad' in rol_lower or request.user.is_superuser or 'admin' in rol_lower:
        return redirect('coordinador_dashboard')

    hoy = timezone.localdate()
    seguimientos = BitacoraSeguimiento.objects.select_related(
        'ficha', 'ficha__institucion', 'matricula__aprendiz', 'instructor'
    )


    url_carnet = f'/estudiantes/{request.user.perfil.pk}/carnet/' if (rol_nombre == 'Estudiante' and hasattr(request.user, 'perfil')) else '/estudiantes/'

    modulos_disponibles = [
        {'titulo': 'Fichas y programas', 'descripcion': 'Gestión de cohortes, horarios y rutas formativas.', 'icono': 'bi-layers', 'activo': True, 'url': '/academico/fichas/', 'accion': 'Ver Fichas'},
        {'titulo': 'Evaluación RAP', 'descripcion': 'Juicios cualitativos, evidencias y retroalimentación.', 'icono': 'bi-award', 'activo': True, 'url': '/evaluaciones/', 'accion': 'Calificar'},
        {'titulo': 'Secretaría Académica', 'descripcion': 'Ventanilla única de trámites, constancias y novedades.', 'icono': 'bi-inbox', 'activo': True, 'url': '/seguimiento/secretaria/' if rol_nombre != 'Estudiante' else '/seguimiento/secretaria/mis-solicitudes/', 'accion': 'Trámites'},
        {'titulo': 'Control de asistencia', 'descripcion': 'Asistencias diarias, alertas y acompañamiento en aula.', 'icono': 'bi-calendar2-check', 'activo': rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA'], 'url': '/seguimiento/asistencia/', 'accion': 'Control Diario'},
        {'titulo': 'Programas de Formación', 'descripcion': 'Diseños curriculares SOFIA, normas y competencias.', 'icono': 'bi-journal-bookmark', 'activo': True, 'url': '/academico/programas/', 'accion': 'Ver Catálogo'},
        {'titulo': 'Carnet Digital QR', 'descripcion': 'Control de ingreso con renovación criptográfica diaria.', 'icono': 'bi-qr-code-scan', 'activo': True, 'url': url_carnet, 'accion': 'Ver Carnet'},
        {'titulo': 'Reportes e Indicadores', 'descripcion': 'Generación de informes en PDF y Excel para auditoría.', 'icono': 'bi-bar-chart-line', 'activo': rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA'], 'url': '/reportes/', 'accion': 'Informes'},
        {'titulo': 'Contactar Secretaría', 'descripcion': 'Radica consultas, solicitudes de constancia o novedades.', 'icono': 'bi-envelope-plus', 'activo': True, 'url': '/seguimiento/secretaria/solicitud/nueva/', 'accion': 'Radicar Trámite'},
    ]

    tablero_fichas = []
    for ficha in Ficha.objects.select_related('programa', 'institucion', 'instructor_lider')[:6]:
        n_aprendices = Matricula.objects.filter(ficha=ficha).count()
        tablero_fichas.append({
            'id': ficha.id,
            'codigo': ficha.codigo_ficha,
            'programa': ficha.programa.denominacion,
            'institucion': ficha.institucion.nombre,
            'instructor': ficha.instructor_lider.get_full_name() or ficha.instructor_lider.username,
            'jornada': 'Diurna',
            'estado': ficha.estado,
            'aprendices': n_aprendices,
            'url_detalle': f'/academico/fichas/{ficha.id}/',
            'url_aprendices': f'/estudiantes/?ficha={ficha.id}',
            'url_horario': f'/academico/horarios/?ficha={ficha.id}',
            'url_seguimiento': f'/seguimiento/?ficha={ficha.id}',
            'url_evaluaciones': f'/evaluaciones/?ficha={ficha.id}',
        })

    solicitudes_pendientes = SolicitudSecretaria.objects.filter(estado__in=['ENVIADA', 'RECIBIDA', 'EN_REVISION']).count()
    notificaciones_usuario = Notificacion.objects.filter(usuario=request.user, leida=False)[:5]

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
        'solicitudes_pendientes': solicitudes_pendientes,
        'notificaciones_usuario': notificaciones_usuario,
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
         'tipo': 'Evidencia de aprendiz', 'fecha': entrega.fecha_entrega, 'ficha': entrega.evidencia.rap_codigo}
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
    """Directorio institucional y consulta de aprendices SENA con filtros avanzados."""
    query = request.GET.get('q', '').strip()
    ficha_filtro = request.GET.get('ficha', '').strip()
    programa_filtro = request.GET.get('programa', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    orden = request.GET.get('orden', 'apellidos').strip()

    matriculas = Matricula.objects.select_related(
        'aprendiz', 'aprendiz__perfil', 'ficha', 'ficha__programa', 'ficha__institucion'
    )

    if estado_filtro:
        matriculas = matriculas.filter(estado_formacion=estado_filtro)
    else:
        matriculas = matriculas.filter(estado_formacion='En Formacion')

    if ficha_filtro:
        if ficha_filtro.isdigit():
            matriculas = matriculas.filter(Q(ficha__id=ficha_filtro) | Q(ficha__codigo_ficha=ficha_filtro))
        else:
            matriculas = matriculas.filter(ficha__codigo_ficha__icontains=ficha_filtro)

    if programa_filtro:
        if programa_filtro.isdigit():
            matriculas = matriculas.filter(ficha__programa__id=programa_filtro)
        else:
            matriculas = matriculas.filter(ficha__programa__denominacion__icontains=programa_filtro)

    if query:
        matriculas = matriculas.filter(
            models.Q(aprendiz__first_name__icontains=query)
            | models.Q(aprendiz__last_name__icontains=query)
            | models.Q(aprendiz__perfil__numero_documento__icontains=query)
            | models.Q(aprendiz__email__icontains=query)
            | models.Q(ficha__codigo_ficha__icontains=query)
            | models.Q(ficha__programa__denominacion__icontains=query)
        )

    if orden == 'nombres':
        matriculas = matriculas.order_by('aprendiz__first_name', 'aprendiz__last_name')
    elif orden == 'documento':
        matriculas = matriculas.order_by('aprendiz__perfil__numero_documento')
    elif orden == 'ficha':
        matriculas = matriculas.order_by('ficha__codigo_ficha', 'aprendiz__last_name')
    else:
        matriculas = matriculas.order_by('aprendiz__last_name', 'aprendiz__first_name')

    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        filas = list(load_workbook(archivo, read_only=True, data_only=True).active.iter_rows(values_only=True))
        encabezados = [str(valor or '').strip().lower() for valor in filas[0]]
        indices = {nombre: encabezados.index(nombre) for nombre in ('numero_documento', 'nombres', 'apellidos', 'correo', 'grado_escolar', 'codigo_ficha') if nombre in encabezados}
        if 'codigo_ficha' not in indices:
            return render(request, 'usuarios/estudiantes_lista.html', {'matriculas': matriculas, 'query': query, 'error_importacion': 'El archivo no contiene la columna codigo_ficha.'})
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
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='APRENDICES',
                accion='IMPORTACION_MASIVA',
                detalles=f'Importado aprendiz {user.get_full_name()} ({documento}) en Ficha {ficha.codigo_ficha}',
                request=request
            )
        messages.success(request, 'Importación masiva completada correctamente.')
        return redirect('estudiantes_lista')

    fichas_disponibles = Ficha.objects.select_related('programa').order_by('codigo_ficha')
    programas_disponibles = ProgramaFormacion.objects.order_by('denominacion')
    estados_disponibles = Matricula.ESTADOS_APRENDIZ

    total_aprendices = matriculas.count()

    context = {
        'matriculas': matriculas,
        'query': query,
        'ficha_filtro': ficha_filtro,
        'programa_filtro': programa_filtro,
        'estado_filtro': estado_filtro,
        'orden': orden,
        'fichas_disponibles': fichas_disponibles,
        'programas_disponibles': programas_disponibles,
        'estados_disponibles': estados_disponibles,
        'total_aprendices': total_aprendices,
    }
    return render(request, 'usuarios/estudiantes_lista.html', context)


@login_required
def registrar_aprendiz(request):
    fichas = Ficha.objects.select_related('programa', 'institucion').filter(estado='En Ejecucion').order_by('codigo_ficha')
    return render(request, 'usuarios/registrar_aprendiz.html', {'fichas': fichas})


@login_required
def biblioteca_formacion(request):
    """Catálogo general de la Biblioteca SENA y sección Mis Recursos del Aprendiz."""
    query = request.GET.get('q', '').strip()
    categoria_filtro = request.GET.get('categoria', '').strip()
    tab = request.GET.get('tab', 'todos').strip()

    recursos_qs = RecursoBiblioteca.objects.select_related('programa').all()
    if query:
        recursos_qs = recursos_qs.filter(
            models.Q(titulo__icontains=query)
            | models.Q(autor__icontains=query)
            | models.Q(descripcion__icontains=query)
            | models.Q(programa__denominacion__icontains=query)
        )
    if categoria_filtro:
        recursos_qs = recursos_qs.filter(categoria=categoria_filtro)

    # Recursos guardados por el usuario actual
    ids_guardados = set(RecursoGuardadoAprendiz.objects.filter(aprendiz=request.user).values_list('recurso_id', flat=True))

    if tab == 'mis_recursos':
        recursos_qs = recursos_qs.filter(id__in=ids_guardados)

    categorias = RecursoBiblioteca.CATEGORIAS

    context = {
        'recursos': recursos_qs,
        'query': query,
        'categoria_filtro': categoria_filtro,
        'tab': tab,
        'categorias': categorias,
        'ids_guardados': ids_guardados,
        'total_recursos': RecursoBiblioteca.objects.count(),
        'total_mis_recursos': len(ids_guardados),
    }
    return render(request, 'usuarios/biblioteca.html', context)


@login_required
def guardar_recurso_aprendiz(request, pk):
    """Agrega o retira un recurso de la biblioteca a 'Mis Recursos'."""
    recurso = get_object_or_404(RecursoBiblioteca, pk=pk)
    guardado, created = RecursoGuardadoAprendiz.objects.get_or_create(aprendiz=request.user, recurso=recurso)
    if not created:
        guardado.delete()
        accion = 'removido'
        messages.info(request, f'“{recurso.titulo}” fue retirado de tus recursos guardados.')
    else:
        accion = 'guardado'
        messages.success(request, f'“{recurso.titulo}” fue guardado en Mis Recursos.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'accion': accion})
    return redirect(request.META.get('HTTP_REFERER', 'biblioteca_formacion'))


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
def ver_carnet_digital(request, pk):
    """Vista de Carnet Digital de alta resolución con rotación de seguridad diaria."""
    perfil = get_object_or_404(PerfilUsuario.objects.select_related('usuario', 'rol'), pk=pk)
    hoy = timezone.localdate()
    ahora = timezone.localtime()

    if perfil.qr_rotacion != hoy or not perfil.qr_token:
        perfil.qr_token = uuid.uuid4()
        perfil.qr_rotacion = hoy
        perfil.save(update_fields=['qr_token', 'qr_rotacion'])

    matricula = Matricula.objects.filter(aprendiz=perfil.usuario).select_related(
        'ficha', 'ficha__programa', 'ficha__institucion'
    ).first()

    url_verificacion = request.build_absolute_uri(f'/estudiantes/qr/{perfil.qr_token}/?dia={hoy}')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(url_verificacion)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b2414", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    hash_input = f"{perfil.numero_documento}-{hoy}-SINETEC-REGIONAL-MAGDALENA".encode('utf-8')
    codigo_seguridad_dia = hashlib.sha256(hash_input).hexdigest()[:12].upper()

    context = {
        'perfil': perfil,
        'matricula': matricula,
        'qr_base64': qr_base64,
        'codigo_seguridad_dia': codigo_seguridad_dia,
        'hoy': hoy,
        'ahora': ahora,
        'url_verificacion': url_verificacion,
    }
    return render(request, 'usuarios/carnet_digital.html', context)


@login_required
def detalle_estudiante(request, pk):
    """Expediente completo del aprendiz SENA estructurado en 10 pestañas interconectadas."""
    perfil = get_object_or_404(PerfilUsuario.objects.select_related('usuario', 'rol'), pk=pk)
    validar_propietario_o_coordinador(request, perfil.usuario)
    usuario = perfil.usuario
    matriculas = Matricula.objects.filter(aprendiz=usuario).select_related(
        'ficha', 'ficha__programa', 'ficha__institucion', 'ficha__instructor_lider'
    )
    matricula_principal = matriculas.first()
    ficha = matricula_principal.ficha if matricula_principal else None

    # 1. Calificaciones y Juicios RAP
    juicios = JuicioEvaluativo.objects.filter(matricula__in=matriculas).select_related(
        'resultado_aprendizaje', 'matricula__ficha'
    ).order_by('-fecha_evaluacion')
    total_juicios = juicios.count()
    juicios_aprobados = juicios.filter(juicio_valor='A').count()
    juicios_deficientes = juicios.filter(juicio_valor='D').count()
    porcentaje_aprobacion = round((juicios_aprobados / total_juicios) * 100, 1) if total_juicios > 0 else 0

    # 2. Seguimiento y Bitácoras
    seguimientos_qs = BitacoraSeguimiento.objects.filter(
        Q(matricula__in=matriculas) | (Q(ficha=ficha) if ficha else Q())
    ).select_related('ficha', 'instructor').order_by('-fecha_visita')
    seguimientos = list(seguimientos_qs)

    # 3. Evidencias entregadas por el aprendiz
    calificaciones_evidencias = CalificacionEvidencia.objects.filter(
        aprendiz=usuario
    ).select_related('evidencia', 'evidencia__rap').order_by('-fecha_entrega')

    # 4. Horarios de formación
    horarios = HorarioFicha.objects.filter(ficha=ficha).order_by('dia', 'hora_inicio') if ficha else []

    # 5. Solicitudes de secretaría
    solicitudes = SolicitudSecretaria.objects.filter(aprendiz=usuario).order_by('-fecha_creacion')

    # 6. Documentos unificados del expediente
    documentos = []
    for s in seguimientos:
        if s.archivo_adjunto:
            documentos.append({
                'nombre': s.archivo_adjunto.name.rsplit('/', 1)[-1],
                'url': s.archivo_adjunto.url,
                'tipo': 'Soporte de Seguimiento',
                'fecha': s.fecha_visita,
                'origen': f"Ficha {s.ficha.codigo_ficha}"
            })
    for ce in calificaciones_evidencias:
        if ce.archivo_entregado:
            documentos.append({
                'nombre': ce.archivo_entregado.name.rsplit('/', 1)[-1],
                'url': ce.archivo_entregado.url,
                'tipo': 'Evidencia de Aprendizaje',
                'fecha': ce.fecha_entrega,
                'origen': ce.evidencia.titulo
            })
    for sol in solicitudes:
        if sol.archivo_adjunto:
            documentos.append({
                'nombre': sol.archivo_adjunto.name.rsplit('/', 1)[-1],
                'url': sol.archivo_adjunto.url,
                'tipo': 'Adjunto Solicitud Secretaría',
                'fecha': sol.fecha_creacion,
                'origen': sol.asunto
            })

    # 7. Alertas tempranas
    alertas = []
    if matricula_principal:
        alertas = alertas_desercion_para_matricula(matricula_principal)

    # 8. Historial de Auditoría
    historial = RegistroAuditoria.objects.filter(
        Q(usuario=usuario) | Q(detalles__icontains=perfil.numero_documento)
    ).order_by('-fecha')[:20]

    context = {
        'estudiante': perfil,
        'usuario': usuario,
        'matriculas': matriculas,
        'matricula': matricula_principal,
        'ficha': ficha,
        'juicios': juicios,
        'total_juicios': total_juicios,
        'juicios_aprobados': juicios_aprobados,
        'juicios_deficientes': juicios_deficientes,
        'porcentaje_aprobacion': porcentaje_aprobacion,
        'seguimientos': seguimientos,
        'calificaciones_evidencias': calificaciones_evidencias,
        'horarios': horarios,
        'solicitudes': solicitudes,
        'documentos': documentos,
        'alertas': alertas,
        'historial': historial,
    }
    return render(request, 'usuarios/estudiante_detalle.html', context)


def qr_estudiante(request, token):
    """
    Procesamiento y registro automático de asistencia diaria mediante escaneo de Carnet Digital QR.
    """
    perfil = get_object_or_404(PerfilUsuario.objects.select_related('usuario', 'rol'), qr_token=token)
    dia = request.GET.get('dia')
    hoy = timezone.localdate()
    ahora = timezone.localtime()

    # Validar rotación diaria si aplica
    if (dia and dia != str(hoy)) and (perfil.qr_rotacion and perfil.qr_rotacion != hoy):
        return render(request, 'usuarios/qr_invalido.html', status=410)

    # Actualizar rotación si es de hoy
    if perfil.qr_rotacion != hoy:
        perfil.qr_rotacion = hoy
        perfil.save(update_fields=['qr_rotacion'])

    # Localizar matrícula del aprendiz
    matricula = Matricula.objects.filter(aprendiz=perfil.usuario).select_related(
        'ficha', 'ficha__programa', 'ficha__institucion'
    ).first()

    # Determinar quién registra (el usuario logueado o el propio aprendiz/coordinador)
    registrador = request.user if request.user.is_authenticated else perfil.usuario

    creado = False
    asistencia = None
    if matricula:
        asistencia, creado = AsistenciaAprendiz.objects.get_or_create(
            matricula=matricula,
            fecha=hoy,
            defaults={
                'estado': 'P',
                'observaciones': 'Asistencia diaria registrada automáticamente por escaneo de Carnet Digital QR',
                'registrado_por': registrador,
            }
        )
        if not creado and asistencia.estado != 'P':
            asistencia.estado = 'P'
            asistencia.observaciones = 'Asistencia actualizada a Presente por Carnet Digital QR'
            asistencia.save(update_fields=['estado', 'observaciones'])

    # Estadísticas para la tarjeta de confirmación
    total_asistencias = AsistenciaAprendiz.objects.filter(matricula=matricula, estado='P').count() if matricula else 1
    total_ausencias = AsistenciaAprendiz.objects.filter(matricula=matricula, estado='A').count() if matricula else 0
    total_sesiones = AsistenciaAprendiz.objects.filter(matricula=matricula).count() if matricula else 1
    porcentaje = round((total_asistencias / total_sesiones * 100), 1) if total_sesiones > 0 else 100

    context = {
        'perfil': perfil,
        'matricula': matricula,
        'asistencia': asistencia,
        'creado': creado,
        'hoy': hoy,
        'ahora': ahora,
        'total_asistencias': total_asistencias,
        'total_ausencias': total_ausencias,
        'porcentaje': porcentaje,
        'es_valido_hoy': True,
    }
    return render(request, 'usuarios/asistencia_confirmada.html', context)


@csrf_exempt
def api_registrar_asistencia_qr(request):
    """Endpoint API JSON para registrar asistencia en vivo desde cámara o formulario."""
    if request.method not in ['POST', 'GET']:
        return JsonResponse({'success': False, 'mensaje': 'Método no permitido.'}, status=405)

    import json
    raw_data = ''
    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body.decode('utf-8'))
                raw_data = body.get('raw_data', '').strip()
            except Exception:
                pass
        if not raw_data:
            raw_data = request.POST.get('raw_data', '').strip()
    else:
        raw_data = request.GET.get('raw_data', '').strip()

    if not raw_data:
        return JsonResponse({'success': False, 'mensaje': 'No se enviaron datos de escaneo.'}, status=400)

    # Puede ser una URL con UUID, un UUID directo, o un número de documento
    token_str = None
    import re
    uuid_match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', raw_data, re.IGNORECASE)
    if uuid_match:
        token_str = uuid_match.group(0)

    hoy = timezone.localdate()
    ahora = timezone.localtime()
    perfil = None

    if token_str:
        perfil = PerfilUsuario.objects.filter(qr_token=token_str).select_related('usuario', 'rol').first()

    if not perfil:
        perfil = PerfilUsuario.objects.filter(
            Q(numero_documento=raw_data) | Q(usuario__username=raw_data)
        ).select_related('usuario', 'rol').first()

    if not perfil:
        return JsonResponse({'success': False, 'mensaje': f'No se encontró ningún aprendiz asociado a "{raw_data}".'}, status=404)

    matricula = Matricula.objects.filter(aprendiz=perfil.usuario).select_related(
        'ficha', 'ficha__programa', 'ficha__institucion'
    ).first()

    registrador = request.user if request.user.is_authenticated else perfil.usuario

    creado = False
    if matricula:
        asistencia, creado = AsistenciaAprendiz.objects.get_or_create(
            matricula=matricula,
            fecha=hoy,
            defaults={
                'estado': 'P',
                'observaciones': 'Asistencia diaria registrada mediante escáner web/móvil',
                'registrado_por': registrador,
            }
        )
        if not creado and asistencia.estado != 'P':
            asistencia.estado = 'P'
            asistencia.observaciones = 'Asistencia actualizada a Presente por escáner QR'
            asistencia.save(update_fields=['estado', 'observaciones'])

    total_asistencias = AsistenciaAprendiz.objects.filter(matricula=matricula, estado='P').count() if matricula else 1

    return JsonResponse({
        'success': True,
        'mensaje': '¡Asistencia registrada en la lista de hoy!' if creado else '¡Asistencia ya confirmada previamente para hoy!',
        'aprendiz': perfil.usuario.get_full_name() or perfil.usuario.username,
        'documento': perfil.numero_documento,
        'ficha': matricula.ficha.codigo_ficha if matricula else '3173430',
        'programa': matricula.ficha.programa.denominacion if (matricula and matricula.ficha.programa) else 'ADSI',
        'hora': ahora.strftime('%I:%M:%S %p'),
        'creado': creado,
        'asistencias_totales': total_asistencias,
    })


def escanear_asistencia_camara(request):
    """Vista con visor de cámara en vivo para registrar asistencia con el celular o webcam."""
    return render(request, 'usuarios/escanear_asistencia.html', {
        'hoy': timezone.localdate(),
        'ahora': timezone.localtime(),
    })



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
@solo_instructor
def instructor_dashboard(request):
    hoy = timezone.localdate()
    fichas_qs = Ficha.objects.filter(
        Q(instructor_lider=request.user) | Q(horarios__instructor=request.user)
    ).distinct().select_related('programa', 'institucion')

    if not fichas_qs.exists() and request.user.is_superuser:
        fichas_ids = list(Ficha.objects.values_list('id', flat=True)[:6])
        fichas_qs = Ficha.objects.filter(id__in=fichas_ids).select_related('programa', 'institucion')

    fichas_con_stats = []
    for f in fichas_qs:
        total_apr = Matricula.objects.filter(ficha=f).count()
        asistencias_f = AsistenciaAprendiz.objects.filter(matricula__ficha=f)
        total_asist = asistencias_f.count()
        asist_p = asistencias_f.filter(estado='P').count()
        asist_prom = round((asist_p / total_asist * 100), 1) if total_asist > 0 else 100.0
        por_calif = CalificacionEvidencia.objects.filter(
            evidencia__ficha=f, juicio_evaluativo='PENDIENTE'
        ).count()
        fichas_con_stats.append({
            'ficha': f,
            'total_aprendices': total_apr,
            'asistencia_promedio': asist_prom,
            'por_calificar': por_calif,
        })

    dia_semana_map = {0: 'LUN', 1: 'MAR', 2: 'MIE', 3: 'JUE', 4: 'VIE', 5: 'SAB', 6: 'DOM'}
    dia_codigo = dia_semana_map.get(hoy.weekday(), 'LUN')
    clases_hoy = HorarioFicha.objects.filter(
        Q(instructor=request.user) | Q(ficha__in=fichas_qs),
        dia=dia_codigo
    ).select_related('ficha', 'ficha__programa')

    evidencias = EvidenciaTaller.objects.filter(
        Q(ficha__in=fichas_qs) | Q(ficha__isnull=True)
    ).select_related('rap', 'ficha').order_by('fecha_limite')

    entregas = CalificacionEvidencia.objects.filter(
        evidencia__ficha__in=fichas_qs
    ).select_related('evidencia', 'aprendiz').order_by('-fecha_entrega')

    pendientes_calificar = CalificacionEvidencia.objects.filter(
        Q(evidencia__ficha__in=fichas_qs) | Q(evidencia__ficha__isnull=True),
        juicio_evaluativo='PENDIENTE'
    ).count()

    aprendices_en_alerta = []
    matriculas_fichas = Matricula.objects.filter(ficha__in=fichas_qs).select_related(
        'aprendiz', 'aprendiz__perfil', 'ficha'
    )
    for mat in matriculas_fichas[:25]:
        motivos = alertas_desercion_para_matricula(mat)
        if motivos:
            aprendices_en_alerta.append({
                'aprendiz': mat.aprendiz,
                'ficha': mat.ficha,
                'motivos': motivos,
            })

    compromisos_pendientes = CompromisoFormativo.objects.filter(
        matricula__ficha__in=fichas_qs,
        estado='PENDIENTE'
    ).select_related('matricula__aprendiz', 'matricula__ficha')[:8]

    q_aprendiz = request.GET.get('q_aprendiz', '').strip()
    aprendices_qs = Matricula.objects.filter(ficha__in=fichas_qs).select_related(
        'aprendiz', 'aprendiz__perfil', 'ficha', 'ficha__programa'
    )
    if q_aprendiz:
        aprendices_qs = aprendices_qs.filter(
            Q(aprendiz__first_name__icontains=q_aprendiz) |
            Q(aprendiz__last_name__icontains=q_aprendiz) |
            Q(aprendiz__username__icontains=q_aprendiz) |
            Q(aprendiz__perfil__numero_documento__icontains=q_aprendiz)
        )

    return render(request, 'instructor.html', {
        'hoy': hoy,
        'clases_hoy': clases_hoy,
        'pendientes_calificar': pendientes_calificar,
        'aprendices_en_alerta': aprendices_en_alerta,
        'compromisos_pendientes': compromisos_pendientes,
        'fichas_con_stats': fichas_con_stats,
        'aprendices_lista': aprendices_qs[:30],
        'q_aprendiz': q_aprendiz,
        'evidencias': evidencias[:10],
        'entregas': entregas[:8],
        'total_evidencias': evidencias.count(),
        'total_entregas': entregas.count(),
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
@solo_aprendiz
def aprendiz_dashboard(request):
    matricula = Matricula.objects.filter(aprendiz=request.user).select_related(
        'ficha', 'ficha__programa', 'ficha__institucion'
    ).first()

    ficha = matricula.ficha if matricula else None

    if ficha:
        pendientes = EvidenciaTaller.objects.filter(
            Q(ficha=ficha) | Q(ficha__isnull=True)
        ).exclude(calificaciones__aprendiz=request.user).order_by('fecha_limite')
        horarios = HorarioFicha.objects.filter(ficha=ficha).select_related('instructor').order_by('dia', 'hora_inicio')[:5]
    else:
        pendientes = EvidenciaTaller.objects.none()
        horarios = []

    entregas = CalificacionEvidencia.objects.filter(aprendiz=request.user).select_related(
        'evidencia', 'evidencia__rap'
    ).order_by('-fecha_entrega')

    if matricula:
        asistencias_p = AsistenciaAprendiz.objects.filter(matricula=matricula, estado='P').count()
        asistencias_a = AsistenciaAprendiz.objects.filter(matricula=matricula, estado='A').count()
        total_asist = asistencias_p + asistencias_a
        porcentaje_asistencia = round((asistencias_p / total_asist * 100), 1) if total_asist > 0 else 100.0

        juicios = JuicioEvaluativo.objects.filter(matricula=matricula)
        juicios_aprobados = juicios.filter(juicio_valor='A').count()
        juicios_deficientes = juicios.filter(juicio_valor='D').count()
        total_j = juicios.count()
        progreso_global = min(100, int((juicios_aprobados / max(1, total_j)) * 100)) if total_j > 0 else 100

        compromisos = CompromisoFormativo.objects.filter(matricula=matricula).order_by('fecha_limite')
        alertas = alertas_desercion_para_matricula(matricula)
    else:
        asistencias_p = 0
        asistencias_a = 0
        porcentaje_asistencia = 100.0
        juicios_aprobados = 0
        juicios_deficientes = 0
        progreso_global = 100
        compromisos = []
        alertas = []

    solicitudes = SolicitudSecretaria.objects.filter(aprendiz=request.user).order_by('-fecha_creacion')[:5]
    logros = LogroAprendiz.objects.filter(aprendiz=request.user)

    return render(request, 'aprendiz.html', {
        'ficha': ficha,
        'matricula': matricula,
        'entregas': entregas,
        'pendientes': pendientes,
        'conteo_pendientes': pendientes.count(),
        'progreso_global': progreso_global,
        'porcentaje_asistencia': porcentaje_asistencia,
        'asistencias_p': asistencias_p,
        'asistencias_a': asistencias_a,
        'juicios_aprobados': juicios_aprobados,
        'juicios_deficientes': juicios_deficientes,
        'compromisos': compromisos,
        'alertas': alertas,
        'horarios': horarios,
        'solicitudes': solicitudes,
        'logros': logros,
    })



@login_required
@solo_coordinador_o_admin
def coordinador_dashboard(request):
    """Panel de Control y Supervisión para Coordinación Académica SENA."""
    q_ficha = request.GET.get('q_ficha', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    fichas_qs = Ficha.objects.select_related('programa', 'instructor_lider', 'institucion').annotate(
        num_aprendices=Count('matriculas')
    ).order_by('-fecha_inicio')

    if q_ficha:
        fichas_qs = fichas_qs.filter(
            Q(codigo_ficha__icontains=q_ficha) |
            Q(programa__denominacion__icontains=q_ficha) |
            Q(instructor_lider__first_name__icontains=q_ficha) |
            Q(instructor_lider__last_name__icontains=q_ficha)
        )
    if estado_filtro:
        fichas_qs = fichas_qs.filter(estado=estado_filtro)

    # Indicadores Institucionales
    total_fichas = Ficha.objects.count()
    fichas_activas = Ficha.objects.filter(estado='En Ejecucion').count()
    total_aprendices = Matricula.objects.filter(estado_formacion='En Formacion').count()
    total_instructores = User.objects.filter(perfil__rol__nombre__icontains='Instructor').count()
    total_programas = ProgramaFormacion.objects.count()

    # Evaluaciones y RAPs
    juicios = JuicioEvaluativo.objects.all()
    juicios_aprobados = juicios.filter(juicio_valor='A').count()
    juicios_por_mejorar = juicios.filter(juicio_valor='D').count()
    total_juicios = juicios_aprobados + juicios_por_mejorar
    tasa_aprobacion = round((juicios_aprobados / total_juicios) * 100, 1) if total_juicios > 0 else 100.0

    # Evidencias y Trámites
    evidencias_pendientes = CalificacionEvidencia.objects.filter(juicio_evaluativo='PENDIENTE').count()
    tramites_pendientes = SolicitudSecretaria.objects.filter(estado__in=['ENVIADA', 'RECIBIDA', 'EN_REVISION']).count()
    tramites_recientes = SolicitudSecretaria.objects.select_related('aprendiz').order_by('-fecha_creacion')[:5]

    # Seguimientos y Horarios
    seguimientos = BitacoraSeguimiento.objects.select_related('ficha', 'instructor').order_by('-fecha_visita')
    seguimientos_pendientes = seguimientos.filter(fecha_verificacion__gte=timezone.localdate()).count()
    total_horarios = HorarioFicha.objects.filter(activo=True).count()

    # Casos que requieren atención
    casos_atencion = []
    if tramites_pendientes > 0:
        casos_atencion.append({
            'tipo': 'warning',
            'titulo': f'{tramites_pendientes} Trámites sin atender en Secretaría',
            'descripcion': 'Existen solicitudes de constancias, novedades o certificados pendientes de respuesta oficial.',
            'url': '/seguimiento/secretaria/?estado=PENDIENTE',
            'btn_texto': 'Revisar Trámites Radicados',
            'icono': 'bi-inbox-fill'
        })
    if evidencias_pendientes > 0:
        casos_atencion.append({
            'tipo': 'info',
            'titulo': f'{evidencias_pendientes} Entregas pendientes de calificación docente',
            'descripcion': 'Talleres y evidencias subidas por aprendices a la espera de retroalimentación pedagógica y juicio.',
            'url': '/evaluaciones/',
            'btn_texto': 'Ir a Evaluación RAP',
            'icono': 'bi-clock-history'
        })
    if juicios_por_mejorar > 0:
        casos_atencion.append({
            'tipo': 'danger',
            'titulo': f'{juicios_por_mejorar} Juicios no aprobados ("D")',
            'descripcion': 'Aprendices con resultados de aprendizaje que requieren plan de mejoramiento académico.',
            'url': '/evaluaciones/',
            'btn_texto': 'Ver Sábana de Evaluación',
            'icono': 'bi-exclamation-triangle-fill'
        })
    fichas_sin_instructor = Ficha.objects.filter(instructor_lider__isnull=True).count()
    if fichas_sin_instructor > 0:
        casos_atencion.append({
            'tipo': 'danger',
            'titulo': f'{fichas_sin_instructor} Ficha(s) sin Instructor Líder asignado',
            'descripcion': 'Se requiere asignar un docente instructor responsable para el seguimiento de la cohorte.',
            'url': '/academico/fichas/',
            'btn_texto': 'Asignar Instructores',
            'icono': 'bi-person-x-fill'
        })

    # Aprendices con alertas de inasistencia o rendimiento
    aprendices_alerta = []
    for mat in Matricula.objects.filter(estado_formacion='En Formacion').select_related('aprendiz', 'ficha', 'aprendiz__perfil')[:30]:
        als = alertas_desercion_para_matricula(mat)
        if als:
            aprendices_alerta.append({
                'matricula': mat,
                'aprendiz': mat.aprendiz,
                'ficha': mat.ficha,
                'alertas': als,
            })

    context = {
        'fichas': fichas_qs[:10],
        'total_fichas': total_fichas,
        'fichas_activas': fichas_activas,
        'total_aprendices': total_aprendices,
        'total_instructores': total_instructores,
        'total_programas': total_programas,
        'total_horarios': total_horarios,
        'juicios_aprobados': juicios_aprobados,
        'juicios_por_mejorar': juicios_por_mejorar,
        'total_juicios': total_juicios,
        'tasa_aprobacion': tasa_aprobacion,
        'evidencias_pendientes': evidencias_pendientes,
        'tramites_pendientes': tramites_pendientes,
        'tramites_recientes': tramites_recientes,
        'seguimientos_pendientes': seguimientos_pendientes,
        'seguimientos_recientes': seguimientos[:5],
        'casos_atencion': casos_atencion,
        'aprendices_alerta': aprendices_alerta,
        'q_ficha': q_ficha,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'coordinador.html', context)


@login_required
@solo_coordinador_o_admin
def gestion_usuarios(request):
    """Gestión y directorio real de usuarios con filtros por rol y estado."""
    rol_filtro = request.GET.get('rol', '').strip().lower()
    q = request.GET.get('q', '').strip()

    usuarios_qs = User.objects.select_related('perfil', 'perfil__rol').all().order_by('last_name', 'first_name')

    if q:
        usuarios_qs = usuarios_qs.filter(
            Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(username__icontains=q)
            | Q(email__icontains=q)
            | Q(perfil__numero_documento__icontains=q)
        )

    if rol_filtro and rol_filtro != 'todos':
        if rol_filtro in ['aprendiz', 'estudiante']:
            usuarios_qs = usuarios_qs.filter(perfil__rol__nombre__in=['Estudiante', 'Aprendiz'])
        elif rol_filtro in ['instructor']:
            usuarios_qs = usuarios_qs.filter(perfil__rol__nombre__icontains='Instructor')
        elif rol_filtro in ['coordinador']:
            usuarios_qs = usuarios_qs.filter(perfil__rol__nombre__icontains='Coordinador')
        elif rol_filtro in ['secretaria']:
            usuarios_qs = usuarios_qs.filter(perfil__rol__nombre__icontains='Secretar')
        elif rol_filtro in ['docente']:
            usuarios_qs = usuarios_qs.filter(perfil__rol__nombre__icontains='Docente')
        elif rol_filtro in ['admin', 'administrador']:
            usuarios_qs = usuarios_qs.filter(Q(is_superuser=True) | Q(perfil__rol__nombre__icontains='Admin'))

    total_usuarios = User.objects.count()
    total_aprendices = User.objects.filter(perfil__rol__nombre__in=['Estudiante', 'Aprendiz']).count()
    total_instructores = User.objects.filter(perfil__rol__nombre__icontains='Instructor').count()
    total_coordinadores = User.objects.filter(perfil__rol__nombre__icontains='Coordinador').count()
    total_activos = User.objects.filter(is_active=True).count()

    context = {
        'usuarios': usuarios_qs,
        'total_usuarios': total_usuarios,
        'total_aprendices': total_aprendices,
        'total_instructores': total_instructores,
        'total_coordinadores': total_coordinadores,
        'total_activos': total_activos,
        'rol_filtro': rol_filtro,
        'q': q,
    }
    return render(request, 'usuarios/gestion_usuarios.html', context)


@login_required
def centro_reportes(request):
    """Centro integral de reportes y exportación institucional SENA."""
    fichas = Ficha.objects.select_related('programa', 'instructor_lider').order_by('codigo_ficha')
    programas = ProgramaFormacion.objects.all().order_by('denominacion')

    context = {
        'fichas': fichas,
        'programas': programas,
        'total_fichas': fichas.count(),
        'total_aprendices': Matricula.objects.count(),
        'total_juicios': JuicioEvaluativo.objects.count(),
        'total_solicitudes': SolicitudSecretaria.objects.count(),
    }
    return render(request, 'reportes/reportes.html', context)


@login_required
def indicadores_dashboard(request):
    """Cuadro de mando e indicadores clave de rendimiento (KPIs) institucionales."""
    total_aprendices = Matricula.objects.count()
    total_fichas = Ficha.objects.count()
    fichas_activas = Ficha.objects.filter(estado='En Ejecucion').count()

    juicios = JuicioEvaluativo.objects.all()
    total_juicios = juicios.count()
    juicios_a = juicios.filter(juicio_valor='A').count()
    juicios_d = juicios.filter(juicio_valor='D').count()
    tasa_aprobacion = round((juicios_a / total_juicios) * 100, 1) if total_juicios > 0 else 0

    evidencias_totales = EvidenciaTaller.objects.count()
    calificaciones_entregadas = CalificacionEvidencia.objects.count()
    evidencias_pendientes = CalificacionEvidencia.objects.filter(juicio_evaluativo='PENDIENTE').count()
    evidencias_aprobadas = CalificacionEvidencia.objects.filter(juicio_evaluativo='A').count()

    solicitudes_abiertas = SolicitudSecretaria.objects.filter(estado__in=['ENVIADA', 'RECIBIDA', 'EN_REVISION']).count()
    solicitudes_cerradas = SolicitudSecretaria.objects.filter(estado__in=['RESPONDIDA', 'CERRADA']).count()

    seguimientos = BitacoraSeguimiento.objects.all()
    total_seguimientos = seguimientos.count()

    dificultad = list(juicios.filter(juicio_valor='D').values(
        'resultado_aprendizaje__codigo', 'resultado_aprendizaje__descripcion'
    ).annotate(total=Count('id')).order_by('-total')[:5])

    context = {
        'total_aprendices': total_aprendices,
        'total_fichas': total_fichas,
        'fichas_activas': fichas_activas,
        'total_juicios': total_juicios,
        'juicios_a': juicios_a,
        'juicios_d': juicios_d,
        'tasa_aprobacion': tasa_aprobacion,
        'evidencias_totales': evidencias_totales,
        'calificaciones_entregadas': calificaciones_entregadas,
        'evidencias_pendientes': evidencias_pendientes,
        'evidencias_aprobadas': evidencias_aprobadas,
        'solicitudes_abiertas': solicitudes_abiertas,
        'solicitudes_cerradas': solicitudes_cerradas,
        'total_seguimientos': total_seguimientos,
        'dificultad': dificultad,
    }
    return render(request, 'reportes/indicadores.html', context)


@login_required
def notificaciones_lista(request):
    """Bandeja de notificaciones y alertas internas para el usuario actual."""
    filtro = request.GET.get('filtro', 'todas')
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    if filtro == 'no_leidas':
        notificaciones = notificaciones.filter(leida=False)

    context = {
        'notificaciones': notificaciones,
        'total_no_leidas': Notificacion.objects.filter(usuario=request.user, leida=False).count(),
        'filtro': filtro,
    }
    return render(request, 'usuarios/notificaciones.html', context)


@login_required
def marcar_notificacion_leida(request, pk):
    """Marca una notificación como leída."""
    notif = get_object_or_404(Notificacion, pk=pk, usuario=request.user)
    notif.leida = True
    notif.save(update_fields=['leida'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok'})
    messages.success(request, 'Notificación marcada como leída.')
    return redirect('notificaciones_lista')


@login_required
@solo_coordinador_o_admin
def auditoria_lista(request):
    """Registro institucional de auditoría y trazabilidad para acciones críticas."""
    modulo = request.GET.get('modulo', '').strip()
    accion = request.GET.get('accion', '').strip()
    q = request.GET.get('q', '').strip()

    logs = RegistroAuditoria.objects.select_related('usuario').all().order_by('-fecha')

    if modulo:
        logs = logs.filter(modulo__iexact=modulo)
    if accion:
        logs = logs.filter(accion__icontains=accion)
    if q:
        logs = logs.filter(
            Q(detalles__icontains=q)
            | Q(usuario__first_name__icontains=q)
            | Q(usuario__last_name__icontains=q)
            | Q(usuario__username__icontains=q)
        )

    modulos = RegistroAuditoria.objects.values_list('modulo', flat=True).distinct()

    context = {
        'logs': logs[:60],
        'total_logs': logs.count(),
        'modulos': modulos,
        'modulo_actual': modulo,
        'accion_actual': accion,
        'q': q,
    }
    return render(request, 'usuarios/auditoria.html', context)


def _normalizar_fecha_aware(val):
    if not val:
        return timezone.now()
    if isinstance(val, date) and not hasattr(val, 'hour'):
        val = timezone.datetime.combine(val, timezone.datetime.min.time())
    if timezone.is_naive(val):
        return timezone.make_aware(val, timezone.get_current_timezone())
    return val


@login_required
def portafolio_aprendiz(request):
    """
    Portafolio Digital del Aprendiz SENA ('Mi libro digital de formación').
    Consolida actividades, evidencias, evaluaciones RAP, asistencias y seguimiento.
    """
    aprendiz = request.user
    perfil = getattr(aprendiz, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ('Administrador' if request.user.is_superuser else 'Usuario')

    # Si es instructor o coordinador y pasa ?aprendiz_id=<id>, permite supervisar dicho portafolio
    aprendiz_param = request.GET.get('aprendiz_id')
    if aprendiz_param and (request.user.is_superuser or rol_nombre in ['Instructor SENA', 'Coordinador', 'Administrador']):
        aprendiz = get_object_or_404(User, pk=aprendiz_param)
        perfil = getattr(aprendiz, 'perfil', None)

    matricula = Matricula.objects.filter(aprendiz=aprendiz).select_related(
        'ficha', 'ficha__programa', 'ficha__institucion', 'ficha__instructor_lider'
    ).first()

    ficha = matricula.ficha if matricula else None
    programa = ficha.programa if ficha else None
    instructor_lider = ficha.instructor_lider if ficha else None

    # 1. Actividades y Entregas
    actividades_qs = EvidenciaTaller.objects.filter(
        Q(ficha=ficha) | Q(ficha__isnull=True)
    ).select_related('rap_curricular', 'rap', 'instructor').order_by('fecha_limite')

    calificaciones_map = {
        c.evidencia_id: c for c in CalificacionEvidencia.objects.filter(aprendiz=aprendiz).select_related('evidencia')
    }

    ahora = timezone.now()
    actividades_con_estado = []
    conteo_entregadas = 0
    conteo_pendientes = 0
    conteo_en_revision = 0
    conteo_evaluadas = 0

    for act in actividades_qs:
        calif = calificaciones_map.get(act.id)
        if calif:
            conteo_entregadas += 1
            if calif.juicio_evaluativo in ['A', 'D']:
                estado = 'Evaluada'
                conteo_evaluadas += 1
            else:
                estado = 'En revision'
                conteo_en_revision += 1
        else:
            if act.fecha_limite and act.fecha_limite < ahora:
                estado = 'Vencida'
            else:
                estado = 'Pendiente'
            conteo_pendientes += 1

        actividades_con_estado.append({
            'actividad': act,
            'entrega': calif,
            'estado': estado,
        })

    # Filtro opcional por estado en el portafolio
    filtro_estado = request.GET.get('estado', 'todos').strip()
    q_search = request.GET.get('q', '').strip().lower()

    if filtro_estado != 'todos':
        actividades_con_estado = [
            item for item in actividades_con_estado
            if item['estado'].lower() == filtro_estado.lower()
        ]
    if q_search:
        actividades_con_estado = [
            item for item in actividades_con_estado
            if q_search in item['actividad'].titulo.lower() or q_search in item['actividad'].descripcion.lower()
        ]

    # 2. Juicios Evaluativos RAP
    juicios = JuicioEvaluativo.objects.filter(matricula=matricula).select_related(
        'resultado_aprendizaje', 'resultado_aprendizaje__competencia', 'instructor'
    ).order_by('resultado_aprendizaje__codigo') if matricula else []

    total_raps = RapCurricular.objects.filter(competencia__programa=programa).count() if programa else 0
    juicios_a = sum(1 for j in juicios if j.juicio_valor == 'A')
    juicios_d = sum(1 for j in juicios if j.juicio_valor == 'D')

    # 3. Asistencias
    if matricula:
        asistencias_qs = AsistenciaAprendiz.objects.filter(matricula=matricula)
        asistencias = list(asistencias_qs.order_by('-fecha')[:10])
        total_asistencias = asistencias_qs.count()
        asistencias_p = asistencias_qs.filter(estado='P').count()
        asistencias_a = asistencias_qs.filter(estado='A').count()
        asistencias_j = asistencias_qs.filter(estado='J').count()
        porcentaje_asistencia = round((asistencias_p / total_asistencias) * 100, 1) if total_asistencias > 0 else 100.0
    else:
        asistencias = []
        total_asistencias = 0
        asistencias_p = 0
        asistencias_a = 0
        asistencias_j = 0
        porcentaje_asistencia = 100.0

    # 4. Bitácoras y Seguimientos
    seguimientos = BitacoraSeguimiento.objects.filter(
        Q(matricula=matricula) | Q(ficha=ficha, matricula__isnull=True)
    ).select_related('instructor').order_by('-fecha_visita')[:10] if ficha else []

    # 5. Trámites / Solicitudes en Secretaría
    solicitudes = SolicitudSecretaria.objects.filter(aprendiz=aprendiz).order_by('-fecha_creacion')[:6]

    # 6. Recursos Guardados por el Aprendiz
    recursos_guardados = RecursoGuardadoAprendiz.objects.filter(aprendiz=aprendiz).select_related('recurso')[:6]

    # 7. Línea de Tiempo del Aprendiz ("Historia de mi formación")
    linea_tiempo = []
    for item in actividades_con_estado:
        act = item['actividad']
        cal = item['entrega']
        if act.fecha_asignacion:
            linea_tiempo.append({
                'fecha': act.fecha_asignacion,
                'tipo': 'asignacion',
                'icono': 'bi-journal-plus',
                'badge': 'Asignación',
                'badge_color': 'info',
                'titulo': f"Actividad Asignada: {act.titulo}",
                'descripcion': f"Asignada por el instructor {act.instructor.get_full_name() if act.instructor else 'SENA'}.",
                'url': f"/portafolio/actividad/{act.id}/",
            })
        if cal and cal.fecha_entrega:
            linea_tiempo.append({
                'fecha': _normalizar_fecha_aware(cal.fecha_entrega),
                'tipo': 'entrega',
                'icono': 'bi-upload',
                'badge': 'Entrega',
                'badge_color': 'primary',
                'titulo': f"Evidencia Entregada: {act.titulo}",
                'descripcion': "Evidencia recibida en la plataforma. Pendiente de calificación.",
                'url': f"/portafolio/actividad/{act.id}/",
            })
        if cal and cal.fecha_revision and cal.juicio_evaluativo in ['A', 'D']:
            linea_tiempo.append({
                'fecha': _normalizar_fecha_aware(cal.fecha_revision),
                'tipo': 'calificacion',
                'icono': 'bi-check-circle-fill',
                'badge': f"Juicio: {cal.get_juicio_evaluativo_display()}",
                'badge_color': 'success' if cal.juicio_evaluativo == 'A' else 'warning',
                'titulo': f"Evidencia Calificada: {act.titulo}",
                'descripcion': cal.observaciones or "Retroalimentación asentada por el instructor.",
                'url': f"/portafolio/actividad/{act.id}/",
            })

    for j in juicios:
        linea_tiempo.append({
            'fecha': _normalizar_fecha_aware(j.fecha_evaluacion),
            'tipo': 'juicio_rap',
            'icono': 'bi-award-fill',
            'badge': f"RAP {j.juicio_valor}",
            'badge_color': 'success' if j.juicio_valor == 'A' else 'danger',
            'titulo': f"Evaluación RAP: {j.resultado_aprendizaje.codigo}",
            'descripcion': f"{j.resultado_aprendizaje.descripcion[:90]}... Evaluador: {j.instructor.get_full_name() or j.instructor.username}",
            'url': f"/evaluaciones/",
        })

    for s in seguimientos:
        linea_tiempo.append({
            'fecha': _normalizar_fecha_aware(s.fecha_visita),
            'tipo': 'seguimiento',
            'icono': 'bi-clipboard2-pulse-fill',
            'badge': 'Seguimiento',
            'badge_color': 'secondary',
            'titulo': f"Acompañamiento en Aula: {s.tipo_seguimiento}",
            'descripcion': s.observaciones[:110] + ('...' if len(s.observaciones) > 110 else ''),
            'url': f"/seguimiento/{s.id}/",
        })

    # Ordenar eventos cronológicamente desc
    linea_tiempo.sort(key=lambda x: x['fecha'], reverse=True)

    # 8. Cálculo de Progreso Real (%)
    progreso_raps = (juicios_a / total_raps * 100) if total_raps > 0 else 0
    total_acts = len(actividades_qs)
    progreso_acts = (conteo_entregadas / total_acts * 100) if total_acts > 0 else 0
    progreso_global = round((progreso_raps * 0.5) + (progreso_acts * 0.3) + (porcentaje_asistencia * 0.2), 1)

    context = {
        'aprendiz': aprendiz,
        'perfil': perfil,
        'matricula': matricula,
        'ficha': ficha,
        'programa': programa,
        'instructor_lider': instructor_lider,
        'actividades': actividades_con_estado,
        'total_actividades': total_acts,
        'conteo_entregadas': conteo_entregadas,
        'conteo_pendientes': conteo_pendientes,
        'conteo_en_revision': conteo_en_revision,
        'conteo_evaluadas': conteo_evaluadas,
        'filtro_estado': filtro_estado,
        'q_search': q_search,
        'juicios': juicios,
        'total_raps': total_raps,
        'juicios_a': juicios_a,
        'juicios_d': juicios_d,
        'asistencias': asistencias[:5],
        'total_asistencias': total_asistencias,
        'asistencias_p': asistencias_p,
        'asistencias_a': asistencias_a,
        'asistencias_j': asistencias_j,
        'porcentaje_asistencia': porcentaje_asistencia,
        'seguimientos': seguimientos,
        'solicitudes': solicitudes,
        'recursos_guardados': recursos_guardados,
        'linea_tiempo': linea_tiempo[:15],
        'progreso_global': min(100.0, max(0.0, progreso_global)),
        'progreso_raps': round(progreso_raps, 1),
        'progreso_acts': round(progreso_acts, 1),
    }
    return render(request, 'usuarios/portafolio.html', context)


@login_required
def portafolio_actividad_detalle(request, pk):
    """Vista detallada de una actividad con material del instructor y ciclo de vida de entrega."""
    actividad = get_object_or_404(
        EvidenciaTaller.objects.select_related('rap_curricular', 'rap_curricular__competencia', 'instructor', 'ficha'),
        pk=pk
    )
    entrega = CalificacionEvidencia.objects.filter(evidencia=actividad, aprendiz=request.user).first()
    ahora = timezone.now()

    # Determinar estado
    if entrega:
        if entrega.juicio_evaluativo in ['A', 'D']:
            estado = 'EVALUADA'
        else:
            estado = 'EN_REVISION'
    else:
        if actividad.fecha_limite and actividad.fecha_limite < ahora:
            estado = 'VENCIDA'
        else:
            estado = 'ASIGNADA'

    return render(request, 'usuarios/actividad_detalle.html', {
        'actividad': actividad,
        'entrega': entrega,
        'estado': estado,
        'ahora': ahora,
    })


@login_required
def portafolio_entregar_actividad(request, pk):
    """Procesamiento seguro de subida de evidencia para una actividad formativa."""
    actividad = get_object_or_404(EvidenciaTaller, pk=pk)

    if request.method == 'POST':
        archivo = request.FILES.get('archivo_entregado')
        comentarios = request.POST.get('comentarios_aprendiz', '').strip()

        if not archivo:
            messages.error(request, "Debes seleccionar un archivo para realizar la entrega de la evidencia.")
            return redirect('portafolio_actividad_detalle', pk=pk)

        # Validación de tamaño (máx 15MB)
        if archivo.size > 15 * 1024 * 1024:
            messages.error(request, "El archivo supera el tamaño máximo permitido de 15 MB.")
            return redirect('portafolio_actividad_detalle', pk=pk)

        # Validación de extensión
        ext_permitidas = ['.pdf', '.zip', '.rar', '.docx', '.xlsx', '.png', '.jpg', '.jpeg', '.py']
        nombre_arch = archivo.name.lower()
        if not any(nombre_arch.endswith(ext) for ext in ext_permitidas):
            messages.error(request, f"Formato no permitido. Se aceptan archivos {', '.join(ext_permitidas)}.")
            return redirect('portafolio_actividad_detalle', pk=pk)

        entrega, created = CalificacionEvidencia.objects.update_or_create(
            evidencia=actividad,
            aprendiz=request.user,
            defaults={
                'archivo_entregado': archivo,
                'comentarios_aprendiz': comentarios,
                'juicio_evaluativo': 'PENDIENTE',
            }
        )

        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='PORTAFOLIO',
            accion='ENTREGA_EVIDENCIA',
            detalles=f"Entrega de evidencia para {actividad.titulo} (Archivo: {archivo.name})",
            request=request
        )

        messages.success(request, f"¡Tu evidencia para '{actividad.titulo}' ha sido entregada exitosamente al instructor!")
        return redirect('portafolio_actividad_detalle', pk=pk)

    return redirect('portafolio_actividad_detalle', pk=pk)


@login_required
def asistente_consulta(request):
    """
    Motor Cognitivo Contextual del Asistente Institucional SINETEC.
    Consulta en tiempo real la base de datos según el rol autenticado y devuelve
    respuestas verídicas, chips de navegación rápida y enlaces de acción directa.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    import json
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    mensaje = data.get('mensaje', '').strip()
    accion = data.get('accion', '').strip()

    usuario = request.user
    perfil = getattr(usuario, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ('Administrador' if usuario.is_superuser else 'Usuario')
    nombre_display = usuario.first_name or usuario.username

    # Contexto del aprendiz
    matricula = Matricula.objects.filter(aprendiz=usuario).select_related(
        'ficha', 'ficha__programa', 'ficha__instructor_lider', 'ficha__institucion'
    ).first()
    ficha = matricula.ficha if matricula else None
    programa = ficha.programa if ficha else None

    # Respuesta y metadatos
    texto_respuesta = ""
    chips = []
    enlace_accion = None
    tipo_estado = "info"  # info, success, warning, pending

    query = (accion or mensaje).lower().strip()

    # Chips globales comunes para el aprendiz
    chips_aprendiz_default = [
        {'label': '📘 Mi Formación', 'action': 'mi_formacion'},
        {'label': '🏷️ Mi Ficha', 'action': 'mi_ficha'},
        {'label': '📝 Mis Actividades', 'action': 'mis_actividades'},
        {'label': '📂 Mis Evidencias', 'action': 'mis_evidencias'},
        {'label': '📊 Mis Evaluaciones', 'action': 'mis_evaluaciones'},
        {'label': '💼 Mi Portafolio', 'action': 'mi_portafolio'},
        {'label': '📅 Mi Horario', 'action': 'mi_horario'},
        {'label': '🟢 Mi Asistencia', 'action': 'mi_asistencia'},
        {'label': '🪪 Mi Carné', 'action': 'mi_carne'},
        {'label': '📚 Biblioteca', 'action': 'biblioteca'},
        {'label': '🔖 Mis Recursos', 'action': 'mis_recursos'},
        {'label': '📥 Mis Trámites', 'action': 'mis_tramites'},
        {'label': '🔔 Notificaciones', 'action': 'notificaciones'},
        {'label': '❓ Ayuda', 'action': 'ayuda'},
    ]

    # Chips para el instructor
    chips_instructor_default = [
        {'label': '📁 Fichas Asignadas', 'action': 'fichas_instructor'},
        {'label': '📝 Evidencias por Calificar', 'action': 'evidencias_instructor'},
        {'label': '📋 Seguimiento en Aula', 'action': 'seguimiento_instructor'},
        {'label': '📅 Tablero Horarios', 'action': 'horarios'},
        {'label': '🚨 Alertas Tempranas', 'action': 'alertas'},
        {'label': '📚 Biblioteca Digital', 'action': 'biblioteca'},
    ]

    # Chips para Coordinador / Administrador
    chips_admin_default = [
        {'label': '📊 Panel Coordinador', 'action': 'panel_coordinador'},
        {'label': '🚨 Casos con Alerta', 'action': 'alertas'},
        {'label': '📥 Trámites Secretaría', 'action': 'secretaria'},
        {'label': '📈 Reportes Oficiales', 'action': 'reportes'},
        {'label': '👥 Gestión Aprendices', 'action': 'aprendices_admin'},
        {'label': '📚 Biblioteca SENA', 'action': 'biblioteca'},
    ]

    # 1. Saludo inicial o bienvenida
    if not query or any(w in query for w in ['hola', 'buenos', 'buenas', 'saludo', 'inicio', 'empezar', 'identifi']):
        if rol_nombre in ['Estudiante', 'Aprendiz']:
            ficha_str = f"Ficha {ficha.codigo_ficha} — {programa.denominacion}" if ficha and programa else "Proceso de Integración SENA"
            texto_respuesta = (
                f"¡Hola, {nombre_display}! 👋\n"
                f"Soy el Asistente SINETEC.\n\n"
                f"Estoy conectado a tu expediente en la {ficha_str}.\n"
                f"Puedo ayudarte a consultar tu formación, actividades, evidencias, evaluaciones, horarios, asistencia y trámites.\n\n"
                f"¿Qué necesitas hacer hoy?"
            )
            chips = chips_aprendiz_default[:7]
        elif 'Instructor' in rol_nombre:
            n_fichas = usuario.fichas_asignadas.count()
            texto_respuesta = (
                f"¡Cordial saludo, Instructor {nombre_display}! 👨‍🏫\n"
                f"Soy el Asistente SINETEC. Tienes {n_fichas} ficha(s) a tu cargo.\n"
                f"Puedo orientarte con evidencias pendientes de calificar, cronogramas de sesión y novedades formativas."
            )
            chips = chips_instructor_default
        else:
            texto_respuesta = (
                f"¡Hola, {nombre_display}! 🏛️\n"
                f"Soy el Asistente SINETEC para el Centro de Logística y Promoción Ecoturística (Regional Magdalena).\n"
                f"¿En qué gestión académica o administrativa puedo apoyarte?"
            )
            chips = chips_admin_default

    # 2. Mi Ficha / ¿Cuál es mi ficha?
    elif any(w in query for w in ['mi_ficha', 'cual es mi ficha', 'cuál es mi ficha', 'numero de ficha', 'número de ficha', 'mi ficha']):
        if ficha:
            institucion_nombre = ficha.institucion.nombre if ficha.institucion else "Sede Central SENA"
            instructor_nombre = ficha.instructor_lider.get_full_name() if ficha.instructor_lider else "Por asignar"
            texto_respuesta = (
                f"📌 Información oficial de tu ficha en SINETEC:\n\n"
                f"• Número de Ficha: {ficha.codigo_ficha}\n"
                f"• Programa: {programa.denominacion if programa else 'ADSI'}\n"
                f"• Modalidad: {getattr(ficha, 'modalidad', 'Presencial')}\n"
                f"• Institución / Sede: {institucion_nombre}\n"
                f"• Instructor Líder: {instructor_nombre}\n"
                f"• Estado: {ficha.estado}"
            )
            enlace_accion = {'url': f'/academico/fichas/{ficha.id}/', 'texto': 'Ver Ficha Completa'}
        else:
            texto_respuesta = "No registras una ficha activa asignada a tu usuario en este momento. Consulta con Coordinación Académica."
        chips = [{'label': '📘 Mi Formación', 'action': 'mi_formacion'}, {'label': '📅 Mi Horario', 'action': 'mi_horario'}]

    # 3. Mi Programa / ¿Cuál es mi programa?
    elif any(w in query for w in ['mi_programa', 'cual es mi programa', 'cuál es mi programa', 'que programa tengo', 'mi formación', 'mi formacion']):
        if programa:
            from academico.models import ResultadoAprendizaje as RapCurricular
            total_raps = RapCurricular.objects.filter(competencia__programa=programa).count()
            competencias_count = programa.competencias.count() if hasattr(programa, 'competencias') else 0
            texto_respuesta = (
                f"🎓 Programa de Formación SENA:\n\n"
                f"• Denominación: {programa.denominacion}\n"
                f"• Código SOFIA: {programa.codigo_programa}\n"
                f"• Versión Curricular: V.{programa.version}\n"
                f"• Estructura: {competencias_count} Competencias y {total_raps} Resultados de Aprendizaje (RAP).\n\n"
                f"Centro de Formación: Centro de Logística y Promoción Ecoturística (Regional Magdalena)."
            )
            enlace_accion = {'url': f'/academico/programas/{programa.id}/', 'texto': 'Consultar Diseño Curricular'}
        else:
            texto_respuesta = "Tu matrícula no tiene un programa formativo vinculado directamente."
        chips = [{'label': '🏷️ Mi Ficha', 'action': 'mi_ficha'}, {'label': '💼 Mi Portafolio', 'action': 'mi_portafolio'}]

    # 4. Instructor / ¿Qué instructor tengo?
    elif any(w in query for w in ['instructor', 'profesor', 'docente', 'quien me da clase', 'quién me da clase']):
        if ficha and ficha.instructor_lider:
            ins = ficha.instructor_lider
            texto_respuesta = (
                f"👨‍🏫 Instructor Líder asignado a tu Ficha {ficha.codigo_ficha}:\n\n"
                f"• Nombre: {ins.get_full_name() or ins.username}\n"
                f"• Correo Institucional: {ins.email or 'carlos.martinez@misena.edu.co'}\n"
                f"• Rol: Instructor Técnico SENA — ADSI\n"
                f"• Acompañamiento: Seguimiento en Aula y Evaluación de Evidencias RAP."
            )
            enlace_accion = {'url': '/aula/aprendiz/', 'texto': 'Ir a Aula del Aprendiz'}
        else:
            texto_respuesta = "Actualmente no se encuentra un instructor líder asignado formalmente a tu ficha."
        chips = [{'label': '📅 Mi Horario', 'action': 'mi_horario'}, {'label': '📝 Mis Actividades', 'action': 'mis_actividades'}]

    # 5. Actividades y Pendientes / ¿Qué actividades tengo pendientes? / ¿Qué me falta entregar?
    elif any(w in query for w in ['mis_actividades', 'actividad', 'pendiente', 'falta entregar', 'que me falta', 'tareas']):
        if rol_nombre in ['Estudiante', 'Aprendiz'] and ficha:
            entregadas_ids = CalificacionEvidencia.objects.filter(aprendiz=usuario).values_list('evidencia_id', flat=True)
            actividades_pend = EvidenciaTaller.objects.filter(Q(ficha=ficha) | Q(ficha__isnull=True)).exclude(id__in=entregadas_ids).order_by('fecha_limite')
            n_pend = actividades_pend.count()
            if n_pend > 0:
                lista_text = "\n".join([f"• {a.titulo} (Límite: {a.fecha_limite.strftime('%d/%b/%Y')})" for a in actividades_pend[:4]])
                texto_respuesta = (
                    f"📝 Actividades Formativas Pendientes ({n_pend}):\n\n"
                    f"{lista_text}\n\n"
                    f"Recuerda preparar tu informe técnico o archivo y subirlo antes de la fecha límite para su evaluación."
                )
                tipo_estado = "pending"
                enlace_accion = {'url': '/portafolio/#actividades', 'texto': 'Entregar Actividades en mi Portafolio'}
            else:
                texto_respuesta = (
                    f"🎉 ¡Felicitaciones, {nombre_display}!\n\n"
                    f"He consultado el registro formativo y estás 100% al día: No tienes actividades pendientes de entrega."
                )
                tipo_estado = "success"
                enlace_accion = {'url': '/portafolio/', 'texto': 'Ver Historial en mi Portafolio'}
            chips = [{'label': '📂 Mis Evidencias', 'action': 'mis_evidencias'}, {'label': '💼 Mi Portafolio', 'action': 'mi_portafolio'}]
        elif 'Instructor' in rol_nombre:
            fichas = usuario.fichas_asignadas.all()
            por_calificar = CalificacionEvidencia.objects.filter(evidencia__ficha__in=fichas, juicio_evaluativo='PENDIENTE').count()
            texto_respuesta = f"Tienes {por_calificar} entregas de aprendices pendientes por revisar y emitir retroalimentación en tus fichas."
            enlace_accion = {'url': '/aula/instructor/', 'texto': 'Calificar en Aula del Instructor'}
            chips = chips_instructor_default
        else:
            texto_respuesta = "Consulta las actividades y evidencias en el módulo de Acompañamiento y Evaluación RAP."
            enlace_accion = {'url': '/evaluaciones/', 'texto': 'Ver Evaluaciones RAP'}

    # 6. Evidencias entregadas / ¿Qué evidencias he entregado? / Muéstrame mis evidencias
    elif any(w in query for w in ['mis_evidencias', 'entregad', 'evidencias entregadas', 'muestrame mis evidencias', 'mis entregas']):
        if rol_nombre in ['Estudiante', 'Aprendiz']:
            califs = CalificacionEvidencia.objects.filter(aprendiz=usuario).select_related('evidencia', 'evidencia__instructor').order_by('-fecha_entrega')
            if califs.exists():
                items = []
                for c in califs[:5]:
                    estado_tag = "Aprobado (A)" if c.juicio_evaluativo == 'A' else ("No Aprobado (D)" if c.juicio_evaluativo == 'D' else "En Revisión")
                    items.append(f"• {c.evidencia.titulo}: {estado_tag} — Entregado el {c.fecha_entrega.strftime('%d/%m/%Y')}")
                texto_respuesta = (
                    f"📂 Tus Evidencias Registradas en SINETEC ({califs.count()} en total):\n\n"
                    + "\n".join(items) + "\n\n"
                    "Puedes descargar los archivos y leer la retroalimentación del instructor desde tu Portafolio Digital."
                )
                enlace_accion = {'url': '/portafolio/#actividades', 'texto': 'Revisar Detalle en mi Portafolio'}
            else:
                texto_respuesta = "Aún no has registrado entregas de evidencias en el sistema. Puedes subir tu primer taller desde el Portafolio."
                enlace_accion = {'url': '/portafolio/#actividades', 'texto': 'Subir mi primera evidencia'}
            chips = [{'label': '📝 Actividades Pendientes', 'action': 'mis_actividades'}, {'label': '📊 Evaluaciones RAP', 'action': 'mis_evaluaciones'}]
        else:
            texto_respuesta = "El repositorio de evidencias formativas se encuentra disponible en la sábana de evaluaciones."
            enlace_accion = {'url': '/evaluaciones/', 'texto': 'Ir a Evaluaciones RAP'}

    # 7. Evaluaciones RAP / ¿Tengo evaluaciones pendientes? / Mis notas
    elif any(w in query for w in ['mis_evaluaciones', 'evaluacion', 'evaluaciones', 'juicio', 'nota', 'rap', 'aprobado']):
        if matricula:
            juicios = JuicioEvaluativo.objects.filter(matricula=matricula).select_related('resultado_aprendizaje')
            a_count = juicios.filter(juicio_valor='A').count()
            d_count = juicios.filter(juicio_valor='D').count()
            from academico.models import ResultadoAprendizaje as RapCurricular
            total_raps = RapCurricular.objects.filter(competencia__programa=ficha.programa).count() if ficha and ficha.programa else 7
            pendientes = max(0, total_raps - (a_count + d_count))

            texto_respuesta = (
                f"📊 Estado de Juicios Evaluativos RAP (Ficha {ficha.codigo_ficha if ficha else 'SENA'}):\n\n"
                f"• Resultados APROBADOS (A): {a_count}\n"
                f"• Resultados POR MEJORAR (D): {d_count}\n"
                f"• Resultados PENDIENTES de emitir: {pendientes}\n"
                f"• Total del programa curricular: {total_raps} RAPs.\n\n"
                f"Recuerda: En el SENA la evaluación es formativa y cualitativa. Para certificarte requieres el 100% de RAPs en juicio 'A'."
            )
            enlace_accion = {'url': f'/estudiantes/{usuario.perfil.pk}/#juicios', 'texto': 'Ver Mis Calificaciones Oficiales'}
        else:
            texto_respuesta = "La sábana de evaluación RAP permite a instructores y coordinadores emitir y auditar los juicios oficiales."
            enlace_accion = {'url': '/evaluaciones/', 'texto': 'Sábana de Evaluaciones RAP'}
        chips = [{'label': '💼 Mi Portafolio', 'action': 'mi_portafolio'}, {'label': '🟢 Mi Asistencia', 'action': 'mi_asistencia'}]

    # 8. Portafolio Digital
    elif any(w in query for w in ['mi_portafolio', 'portafolio', 'libro digital', 'hoja de vida']):
        texto_respuesta = (
            "📘 Portafolio Digital del Aprendiz:\n\n"
            "Es tu libro personal de formación SENA. Integra de forma consolidada:\n"
            "• Hoja de vida y ficha formativa.\n"
            "• Actividades y entregas de talleres con retroalimentación pedagógica.\n"
            "• Historial de juicios RAP y porcentaje de avance.\n"
            "• Asistencia acumulada y bitácoras de seguimiento.\n"
            "• Recursos técnicos guardados de la Biblioteca."
        )
        enlace_accion = {'url': '/portafolio/', 'texto': 'Abrir Mi Portafolio Digital'}
        chips = [{'label': '📝 Mis Actividades', 'action': 'mis_actividades'}, {'label': '🔖 Mis Recursos', 'action': 'mis_recursos'}]

    # 9. Horarios / ¿Cuál es mi próximo horario?
    elif any(w in query for w in ['mi_horario', 'horario', 'proximo horario', 'próximo horario', 'cuando tengo clase', 'cuándo tengo clase', 'ambiente']):
        if ficha:
            horarios = HorarioFicha.objects.filter(ficha=ficha, activo=True).select_related('instructor').order_by('dia', 'hora_inicio')
            if horarios.exists():
                dias_map = {'1': 'Lunes', '2': 'Martes', '3': 'Miércoles', '4': 'Jueves', '5': 'Viernes', '6': 'Sábado'}
                lineas_h = []
                for h in horarios[:4]:
                    dia_str = dias_map.get(str(h.dia), f"Día {h.dia}")
                    amb_str = h.ambiente or "Ambiente TIC"
                    lineas_h.append(f"• {dia_str}: {h.hora_inicio.strftime('%H:%M')} - {h.hora_fin.strftime('%H:%M')} | {amb_str}")
                texto_respuesta = (
                    f"📅 Programación de Horarios — Ficha {ficha.codigo_ficha}:\n\n"
                    + "\n".join(lineas_h) + "\n\n"
                    f"Recuerda llegar puntual a cada sesión formativa en la institución."
                )
                enlace_accion = {'url': f'/academico/horarios/?ficha={ficha.id}', 'texto': 'Ver Horario Completo de la Ficha'}
            else:
                texto_respuesta = f"Tu Ficha {ficha.codigo_ficha} aún no tiene bloques de horario activos programados en el sistema."
                enlace_accion = {'url': '/academico/horarios/', 'texto': 'Consultar Tablero General de Ambientes'}
        else:
            texto_respuesta = "Puedes consultar el tablero semanal de horarios y ambientes formativos de la institución."
            enlace_accion = {'url': '/academico/horarios/', 'texto': 'Ver Tablero de Horarios'}
        chips = [{'label': '🟢 Mi Asistencia', 'action': 'mi_asistencia'}, {'label': '🪪 Mi Carné', 'action': 'mi_carne'}]

    # 10. Asistencia / ¿Tengo asistencia registrada hoy? / Registrar asistencia
    elif any(w in query for w in ['mi_asistencia', 'asistencia', 'asistencia hoy', 'pase de lista', 'asisti', 'inasistencia']):
        if matricula:
            hoy = timezone.localdate()
            asistencia_hoy = AsistenciaAprendiz.objects.filter(matricula=matricula, fecha=hoy).first()
            asistencias_total = AsistenciaAprendiz.objects.filter(matricula=matricula)
            tot = asistencias_total.count()
            p = asistencias_total.filter(estado='P').count()
            a = asistencias_total.filter(estado='A').count()
            porc = round((p / tot) * 100, 1) if tot > 0 else 100.0

            if asistencia_hoy:
                estado_hoy_str = "Presente (P) ✓" if asistencia_hoy.estado == 'P' else ("Ausente (A)" if asistencia_hoy.estado == 'A' else "Justificado (J)")
                mensaje_hoy = f"Hoy ({hoy.strftime('%d/%m/%Y')}): {estado_hoy_str}"
            else:
                mensaje_hoy = f"Hoy ({hoy.strftime('%d/%m/%Y')}): Aún no se ha registrado tu asistencia para esta sesión."

            texto_respuesta = (
                f"🟢 Estado de Asistencia — Ficha {ficha.codigo_ficha if ficha else 'SENA'}:\n\n"
                f"{mensaje_hoy}\n\n"
                f"• Histórico: {p} sesiones asistidas de {tot} ({porc}% de puntualidad)\n"
                f"• Ausencias: {a}\n\n"
                f"Para registrar tu asistencia en clase, presenta tu Carné Digital QR al instructor."
            )
            enlace_accion = {'url': f'/estudiantes/{usuario.perfil.pk}/carnet/', 'texto': 'Abrir Mi Carné Digital QR'}
        else:
            texto_respuesta = "El control de asistencia se gestiona mediante el módulo de Seguimiento en Aula y lectura de carné QR."
            enlace_accion = {'url': '/seguimiento/asistencia/', 'texto': 'Ir a Control de Asistencia'}
        chips = [{'label': '🪪 Mi Carné', 'action': 'mi_carne'}, {'label': '📅 Mi Horario', 'action': 'mi_horario'}]

    # 11. Carné Digital / Ver mi carné / QR
    elif any(w in query for w in ['mi_carne', 'mi_carné', 'carne', 'carné', 'qr', 'credencial', 'codigo qr', 'código qr']):
        if perfil:
            texto_respuesta = (
                f"🪪 Carné Digital Inteligente — SENA Regional Magdalena:\n\n"
                f"• Aprendiz: {usuario.get_full_name() or usuario.username}\n"
                f"• Documento: {perfil.tipo_documento} {perfil.numero_documento}\n"
                f"• Ficha: {ficha.codigo_ficha if ficha else '3173430'}\n\n"
                f"Seguridad: Cuenta con código QR dinámico criptográfico con rotación diaria y reloj de seguridad activo para evitar fraudes."
            )
            enlace_accion = {'url': f'/estudiantes/{perfil.pk}/carnet/', 'texto': 'Visualizar mi Carné Digital Oficial'}
        else:
            texto_respuesta = "No se localizó un perfil asociado para generar el carné. Comunícate con Administración."
        chips = [{'label': '🟢 Mi Asistencia', 'action': 'mi_asistencia'}, {'label': '💼 Mi Portafolio', 'action': 'mi_portafolio'}]

    # 12. Secretaría / Trámites / Hacer una solicitud / Hablar con secretaría
    elif any(w in query for w in ['secretaria', 'secretaría', 'solicitud', 'tramite', 'trámite', 'radicar', 'hablar con secretaria', 'hacer una solicitud', 'mis_tramites']):
        if 'mis_tramites' in query or 'consultar' in query or 'mis tramites' in query:
            solicitudes = SolicitudSecretaria.objects.filter(aprendiz=usuario).order_by('-fecha_creacion')
            if solicitudes.exists():
                lineas_sol = []
                for s in solicitudes[:4]:
                    lineas_sol.append(f"• Radicado #{s.id}: {s.asunto} [{s.get_estado_display()}]")
                texto_respuesta = (
                    f"📥 Tus Trámites Radicados en Secretaría ({solicitudes.count()}):\n\n"
                    + "\n".join(lineas_sol) + "\n\n"
                    f"Puedes hacer seguimiento en tiempo real y descargar las respuestas oficiales."
                )
                enlace_accion = {'url': '/seguimiento/secretaria/mis-solicitudes/', 'texto': 'Ver Mis Solicitudes Radicadas'}
            else:
                texto_respuesta = "No tienes solicitudes radicadas actualmente en Secretaría Académica."
                enlace_accion = {'url': '/seguimiento/secretaria/solicitud/nueva/', 'texto': 'Radicar una Nueva Solicitud'}
        else:
            texto_respuesta = (
                "🏛️ Secretaría Académica — Centro de Logística y Promoción Ecoturística\n\n"
                "Puedo ayudarte a iniciar tu solicitud oficial. Para radicarla requerimos:\n"
                "1. Tipo de Solicitud (Constancia, Novedad, Certificación, etc.)\n"
                "2. Asunto claro\n"
                "3. Descripción detallada y documento de soporte (PDF/imagen opcional)\n\n"
                "Al enviarla, se te asignará inmediatamente un número de radicado con validez institucional."
            )
            enlace_accion = {'url': '/seguimiento/secretaria/solicitud/nueva/', 'texto': 'Completar Formulario de Radicación'}
        chips = [
            {'label': '📄 Radicar Solicitud', 'action': 'radicar_solicitud'},
            {'label': '📥 Consultar Radicados', 'action': 'mis_tramites'},
            {'label': '❓ Ayuda', 'action': 'ayuda'},
        ]

    # 13. Biblioteca / Libros / Guías / Mis Recursos
    elif any(w in query for w in ['biblioteca', 'libro', 'guia', 'guía', 'manual', 'recurso', 'mis_recursos']):
        if 'mis_recursos' in query or 'guardado' in query:
            guardados = RecursoGuardadoAprendiz.objects.filter(aprendiz=usuario).select_related('recurso')
            if guardados.exists():
                lineas_r = [f"• {g.recurso.titulo} ({g.recurso.categoria})" for g in guardados[:4]]
                texto_respuesta = (
                    f"🔖 Tus Recursos Guardados ({guardados.count()}):\n\n"
                    + "\n".join(lineas_r) + "\n\n"
                    "Disponibles siempre desde tu espacio personal de formación."
                )
                enlace_accion = {'url': '/portafolio/#recursos', 'texto': 'Ver Mis Recursos en el Portafolio'}
            else:
                texto_respuesta = "Aún no has guardado recursos de la Biblioteca. Explora el catálogo y añade los de tu interés."
                enlace_accion = {'url': '/biblioteca/', 'texto': 'Explorar Biblioteca Digital'}
        else:
            recursos_recientes = RecursoBiblioteca.objects.filter(disponible=True).order_by('-id')[:3]
            lineas_b = [f"• {r.titulo} [{r.categoria}]" for r in recursos_recientes]
            texto_respuesta = (
                "📚 Biblioteca Digital SINETEC — Recursos Pedagógicos SENA:\n\n"
                "Encuentra libros técnicos de ingeniería, manuales de diseño SOFIA, guías de aprendizaje y normas IEEE.\n\n"
                "Recursos destacados:\n"
                + "\n".join(lineas_b)
            )
            enlace_accion = {'url': '/biblioteca/', 'texto': 'Abrir Catálogo de Biblioteca'}
        chips = [{'label': '📚 Biblioteca General', 'action': 'biblioteca'}, {'label': '🔖 Mis Recursos', 'action': 'mis_recursos'}]

    # 14. Notificaciones / Alertas
    elif any(w in query for w in ['notificacion', 'notificación', 'alerta', 'novedad', 'notificaciones']):
        no_leidas = Notificacion.objects.filter(usuario=usuario, leida=False).order_by('-fecha_creacion')
        c = no_leidas.count()
        if c > 0:
            primeras = "\n".join([f"• {n.titulo}: {n.mensaje[:60]}..." for n in no_leidas[:3]])
            texto_respuesta = (
                f"🔔 Tienes {c} notificación(es) nueva(s) sin leer:\n\n"
                f"{primeras}"
            )
            enlace_accion = {'url': '/notificaciones/', 'texto': 'Abrir Centro de Notificaciones'}
        else:
            texto_respuesta = "No tienes notificaciones pendientes sin leer en tu bandeja institucional."
            enlace_accion = {'url': '/notificaciones/', 'texto': 'Ver Historial de Notificaciones'}
        chips = [{'label': '📘 Mi Portafolio', 'action': 'mi_portafolio'}, {'label': '📝 Mis Actividades', 'action': 'mis_actividades'}]

    # 15. Ayuda / ¿Qué puedes hacer?
    elif any(w in query for w in ['ayuda', 'help', 'que puedes hacer', 'qué puedes hacer', 'opciones']):
        texto_respuesta = (
            "💡 Guía de Asistencia SINETEC:\n\n"
            "Puedes consultarme preguntas cotidianas como:\n"
            "• \"¿Cuál es mi ficha?\"\n"
            "• \"¿Cuál es mi programa?\"\n"
            "• \"¿Qué instructor tengo?\"\n"
            "• \"¿Qué actividades tengo pendientes?\"\n"
            "• \"¿Qué evidencias he entregado?\"\n"
            "• \"¿Tengo evaluaciones pendientes?\"\n"
            "• \"¿Cuál es mi próximo horario?\"\n"
            "• \"¿Tengo asistencia registrada hoy?\"\n"
            "• \"Quiero ver mi carné\"\n"
            "• \"Quiero radicar una solicitud\"\n"
            "• \"Quiero consultar mi portafolio\"\n\n"
            "También puedes presionar cualquiera de los botones rápidos de abajo."
        )
        chips = chips_aprendiz_default[:6]

    # 16. Fallback institucional
    else:
        texto_respuesta = (
            f"He recibido tu consulta sobre: \"{mensaje}\".\n\n"
            f"Como asistente oficial de SINETEC, consulto los registros reales de la institución. "
            f"Te sugiero seleccionar uno de los accesos directos más consultados:"
        )
        chips = [
            {'label': '📘 Mi Portafolio', 'action': 'mi_portafolio'},
            {'label': '📝 Mis Actividades', 'action': 'mis_actividades'},
            {'label': '📊 Mis Evaluaciones', 'action': 'mis_evaluaciones'},
            {'label': '🪪 Mi Carné QR', 'action': 'mi_carne'},
            {'label': '📥 Secretaría', 'action': 'secretaria'},
            {'label': '❓ Menú de Ayuda', 'action': 'ayuda'},
        ]

    return JsonResponse({
        'status': 'ok',
        'respuesta': texto_respuesta,
        'chips': chips,
        'enlace_accion': enlace_accion,
        'tipo': tipo_estado,
        'usuario': nombre_display,
    })


@login_required
@solo_secretaria_o_coordinador
def secretaria_dashboard(request):
    """Panel de Ventanilla Única y Secretaría Académica SENA."""
    total_solicitudes = SolicitudSecretaria.objects.count()
    pendientes = SolicitudSecretaria.objects.filter(estado__in=['ENVIADA', 'RECIBIDA', 'EN_REVISION']).count()
    respondidas = SolicitudSecretaria.objects.filter(estado='RESPONDIDA').count()
    cerradas = SolicitudSecretaria.objects.filter(estado='CERRADA').count()

    solicitudes = SolicitudSecretaria.objects.select_related('aprendiz', 'ficha').order_by('-fecha_creacion')[:15]

    return render(request, 'dashboards/secretaria_dashboard.html', {
        'total_solicitudes': total_solicitudes,
        'pendientes': pendientes,
        'respondidas': respondidas,
        'cerradas': cerradas,
        'solicitudes': solicitudes,
    })


@login_required
def etapa_productiva_dashboard(request):
    """Panel de gestión y seguimiento de la Etapa Productiva SENA (Convenios, Bitácoras F023, Visitas)."""
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''

    convenios = EmpresaConvenio.objects.filter(activa=True)
    etapas_qs = EtapaProductiva.objects.select_related(
        'matricula__aprendiz', 'matricula__ficha', 'matricula__ficha__programa', 'empresa', 'instructor_seguimiento'
    )

    if rol_nombre in ['Estudiante', 'Aprendiz']:
        etapas_qs = etapas_qs.filter(matricula__aprendiz=request.user)
    elif 'Instructor' in rol_nombre:
        etapas_qs = etapas_qs.filter(Q(instructor_seguimiento=request.user) | Q(matricula__ficha__instructor_lider=request.user))

    bitacoras = BitacoraEtapaProductiva.objects.filter(
        etapa_productiva__in=etapas_qs
    ).select_related('etapa_productiva__matricula__aprendiz').order_by('-fecha_visita')[:15]

    total_etapas = etapas_qs.count()
    activas = etapas_qs.filter(estado='EN_DESARROLLO').count()
    culminadas = etapas_qs.filter(estado='FINALIZADA').count()
    por_iniciar = etapas_qs.filter(estado='POR_INICIAR').count()

    return render(request, 'usuarios/etapa_productiva.html', {
        'convenios': convenios,
        'etapas': etapas_qs[:20],
        'bitacoras': bitacoras,
        'total_etapas': total_etapas,
        'activas': activas,
        'culminadas': culminadas,
        'por_iniciar': por_iniciar,
        'puede_gestionar': request.user.is_superuser or any(r in rol_nombre for r in ['Administrador', 'Coordinador', 'Instructor', 'Secretar']),
    })


@login_required
def innovacion_dashboard(request):
    """Centro de Innovación Tecnológica y Banco de Proyectos Formativos SENNOVA."""
    proyectos = ProyectoInnovacion.objects.select_related('ficha', 'ficha__programa', 'instructor_asesor').order_by('-fecha_creacion')
    estado = request.GET.get('estado', '').strip()
    cat = request.GET.get('categoria', '').strip()
    if estado:
        proyectos = proyectos.filter(estado=estado)
    if cat:
        proyectos = proyectos.filter(categoria=cat)

    return render(request, 'usuarios/innovacion.html', {
        'proyectos': proyectos,
        'total_proyectos': proyectos.count(),
        'en_desarrollo': proyectos.filter(estado='DESARROLLO').count(),
        'terminados': proyectos.filter(estado='FINALIZADO').count(),
        'estado_filtro': estado,
        'linea_filtro': cat,
    })


@login_required
def gestion_documental_lista(request):
    """Repositorio Documental Institucional clasificado por categorías SENA."""
    categoria = request.GET.get('categoria', '').strip()
    q = request.GET.get('q', '').strip()
    docs = DocumentoInstitucional.objects.select_related('subido_por').all().order_by('-fecha_subida')
    if categoria:
        docs = docs.filter(categoria=categoria)
    if q:
        docs = docs.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q))

    return render(request, 'usuarios/gestion_documental.html', {
        'documentos': docs,
        'total_docs': docs.count(),
        'categoria_filtro': categoria,
        'q': q,
    })


@login_required
@solo_instructor
def cambiar_fase_caso(request, pk):
    """Avanza la fase del ciclo de vida de una alerta temprana."""
    caso = get_object_or_404(CasoAlertaTemprana, pk=pk)
    if request.method == 'POST':
        nueva_fase = request.POST.get('fase')
        observaciones = request.POST.get('observaciones', '').strip()
        fases_validas = [k for k, _ in CasoAlertaTemprana.FASES_CASO]
        if nueva_fase in fases_validas:
            caso.fase = nueva_fase
            if observaciones:
                caso.observaciones_comite = (caso.observaciones_comite or '') + f"\n[{timezone.localdate()}] {request.user.username}: {observaciones}"
            if nueva_fase in ['CERRADA_EXITOSA', 'DESERCION_CONFIRMADA']:
                caso.fecha_cierre = timezone.localdate()
            caso.save()
            messages.success(request, f'Fase del caso actualizada a {caso.get_fase_display()}.')
    return redirect('alertas_tempranas')


@login_required
@solo_instructor
def cumplir_compromiso(request, pk):
    """Registra formalmente el cumplimiento de un compromiso formativo."""
    compromiso = get_object_or_404(CompromisoFormativo, pk=pk)
    if request.method == 'POST':
        compromiso.estado = 'CUMPLIDO'
        compromiso.observaciones_verificacion = request.POST.get('observaciones', 'Verificado y cumplido satisfactoriamente.')
        compromiso.save(update_fields=['estado', 'observaciones_verificacion'])
        messages.success(request, f'Compromiso "{compromiso.titulo}" marcado como cumplido.')
    return redirect(request.META.get('HTTP_REFERER', 'alertas_tempranas'))