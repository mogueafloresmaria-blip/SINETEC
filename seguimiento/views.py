from datetime import date
import base64
import binascii
import os
from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.core.paginator import Paginator
from django.db.models import Q, Count
from reportlab.platypus import Image as PDFImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from .models import (
    AsistenciaAprendiz, BitacoraSeguimiento, MensajeSeguimiento,
    SolicitudSecretaria, RespuestaSolicitud, Notificacion, RegistroAuditoria,
    SeguimientoAdministrativo, EventoCalendario, DocumentoAdministrativo
)
from .forms import (
    BitacoraSeguimientoForm, SeguimientoAdministrativoForm,
    EventoCalendarioForm, DocumentoAdministrativoForm
)
from academico.models import Ficha, Matricula, ProgramaFormacion
from instituciones.models import InstitucionEducativa
from convenios.models import ConvenioSENA
from usuarios.decorators import requerir_roles
from django.contrib.auth.models import User



@login_required
def lista_seguimientos(request):
    """
    Historial general de bitácoras de visitas técnicas y acompañamiento.
    Incluye 4 KPIs, filtros multicriterio y paginación.
    """
    query = request.GET.get('q', '').strip()
    institucion_id = request.GET.get('institucion', '').strip()
    ficha_id = request.GET.get('ficha', '').strip()
    usuario_id = request.GET.get('usuario', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    fecha_filtro = request.GET.get('fecha', '').strip()

    # 4 KPIs Administrativos
    total_seguimientos = BitacoraSeguimiento.objects.count()
    seguimientos_pendientes = BitacoraSeguimiento.objects.filter(estado='Pendiente').count()
    seguimientos_en_proceso = BitacoraSeguimiento.objects.filter(estado='En Proceso').count()
    seguimientos_realizados = BitacoraSeguimiento.objects.filter(estado='Realizado').count()

    seguimientos = BitacoraSeguimiento.objects.select_related(
        'ficha', 'ficha__institucion', 'ficha__programa', 'instructor', 'matricula__aprendiz'
    ).all().order_by('-fecha_visita', '-fecha_registro')

    if query:
        seguimientos = seguimientos.filter(
            Q(ficha__codigo_ficha__icontains=query) |
            Q(ficha__programa__denominacion__icontains=query) |
            Q(ficha__institucion__nombre__icontains=query) |
            Q(observaciones__icontains=query) |
            Q(compromisos__icontains=query) |
            Q(instructor__first_name__icontains=query) |
            Q(instructor__last_name__icontains=query) |
            Q(instructor__username__icontains=query)
        )

    if institucion_id:
        seguimientos = seguimientos.filter(ficha__institucion_id=institucion_id)

    if ficha_id:
        seguimientos = seguimientos.filter(ficha_id=ficha_id)

    if usuario_id:
        seguimientos = seguimientos.filter(instructor_id=usuario_id)

    if estado_filtro:
        seguimientos = seguimientos.filter(estado=estado_filtro)

    if fecha_filtro:
        seguimientos = seguimientos.filter(fecha_visita=fecha_filtro)

    instituciones = InstitucionEducativa.objects.filter(activa=True).order_by('nombre')
    fichas = Ficha.objects.all().order_by('codigo_ficha')
    instructores = User.objects.filter(
        Q(seguimientos_registrados__isnull=False) |
        Q(perfil__rol__nombre__icontains='Instructor')
    ).distinct().order_by('first_name', 'last_name')

    hoy = timezone.localdate()
    seguimientos_data = [
        {
            'bitacora': bitacora,
            'estado_compromiso': (
                'vencido' if bitacora.compromisos and bitacora.fecha_verificacion and bitacora.fecha_verificacion < hoy
                else 'por_vencer' if bitacora.compromisos and bitacora.fecha_verificacion
                else 'sin_compromiso'
            ),
        }
        for bitacora in seguimientos
    ]

    paginator = Paginator(seguimientos_data, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    params = request.GET.copy()
    if 'page' in params:
        del params['page']
    active_filters_querystring = params.urlencode()

    context = {
        'page_obj': page_obj,
        'seguimientos': page_obj,
        'total_registros': len(seguimientos_data),
        'total_seguimientos': total_seguimientos,
        'seguimientos_pendientes': seguimientos_pendientes,
        'seguimientos_en_proceso': seguimientos_en_proceso,
        'seguimientos_realizados': seguimientos_realizados,
        'instituciones': instituciones,
        'fichas': fichas,
        'instructores': instructores,
        'busqueda': query,
        'institucion_seleccionada': institucion_id,
        'ficha_seleccionada': ficha_id,
        'usuario_seleccionado': usuario_id,
        'estado_seleccionado': estado_filtro,
        'fecha_seleccionada': fecha_filtro,
        'active_filters_querystring': active_filters_querystring,
    }
    return render(request, 'seguimiento/lista.html', context)


@login_required
def control_asistencia(request):
    ficha_id = request.GET.get('ficha', '').strip()
    fecha_param = request.GET.get('fecha', '').strip()
    try:
        fecha = date.fromisoformat(fecha_param) if fecha_param else timezone.localdate()
    except ValueError:
        fecha = timezone.localdate()

    fichas = Ficha.objects.select_related('programa', 'institucion').order_by('codigo_ficha')
    ficha = get_object_or_404(fichas, pk=ficha_id) if ficha_id else None
    matriculas = []
    asistencias = {}

    if ficha:
        matriculas = list(ficha.matriculas.select_related('aprendiz', 'aprendiz__perfil').filter(
            estado_formacion='En Formacion'
        ).order_by('aprendiz__last_name', 'aprendiz__first_name'))
        asistencias = {
            asistencia.matricula_id: asistencia.estado
            for asistencia in AsistenciaAprendiz.objects.filter(matricula__in=matriculas, fecha=fecha)
        }

    if request.method == 'POST' and ficha:
        estados_validos = {'P', 'A', 'J'}
        with transaction.atomic():
            for matricula in matriculas:
                estado = request.POST.get(f'asistencia_{matricula.pk}', 'P')
                if estado in estados_validos:
                    AsistenciaAprendiz.objects.update_or_create(
                        matricula=matricula,
                        fecha=fecha,
                        defaults={'estado': estado, 'registrado_por': request.user},
                    )
        messages.success(request, f'Asistencia del {fecha:%d/%m/%Y} guardada para {len(matriculas)} aprendices.')
        return redirect(f'/seguimiento/asistencia/?ficha={ficha.pk}&fecha={fecha.isoformat()}')

    return render(request, 'seguimiento/asistencia.html', {
        'fichas': fichas,
        'ficha': ficha,
        'fecha': fecha,
        'matriculas': matriculas,
        'asistencias': asistencias,
        'filas_asistencia': [
            {'matricula': matricula, 'estado': asistencias.get(matricula.pk, 'P')}
            for matricula in matriculas
        ],
    })


@login_required
def nuevo_seguimiento(request):
    """
    Registro de una nueva bitácora de seguimiento con adjunto y validación RN-006.
    """
    ficha_param = request.GET.get('ficha', None)

    if request.method == 'POST':
        form = BitacoraSeguimientoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                latitud, longitud, precision = validar_coordenadas(request.POST)
                firma_instructor = decodificar_firma(request.POST.get('firma_instructor', ''), 'firma_instructor')
                firma_docente = decodificar_firma(request.POST.get('firma_docente_enlace', ''), 'firma_docente_enlace')
            except ValueError as error:
                messages.error(request, str(error))
                return render(request, 'seguimiento/formulario.html', {'form': form, 'titulo': 'Registrar Bitácora de Visita / Seguimiento'})
            bitacora = form.save(commit=False)
            bitacora.instructor = request.user
            bitacora.latitud = latitud
            bitacora.longitud = longitud
            bitacora.precision_gps = precision
            bitacora.save()
            bitacora.firma_instructor.save(firma_instructor[0], firma_instructor[1], save=False)
            bitacora.firma_docente_enlace.save(firma_docente[0], firma_docente[1], save=False)
            bitacora.save(update_fields=['firma_instructor', 'firma_docente_enlace'])
            messages.success(request, f"Bitácora de seguimiento del {bitacora.fecha_visita} guardada exitosamente.")
            return redirect('seguimiento_detalle', pk=bitacora.pk)
        else:
            messages.error(request, "Por favor revise los campos del formulario. Si registró compromisos, debe indicar fecha límite (RN-006).")
    else:
        form = BitacoraSeguimientoForm(ficha_id=ficha_param)

    return render(request, 'seguimiento/formulario.html', {'form': form, 'titulo': 'Registrar Bitácora de Visita / Seguimiento'})


def validar_coordenadas(datos):
    try:
        latitud = Decimal(datos.get('latitud_gps', ''))
        longitud = Decimal(datos.get('longitud_gps', ''))
        precision = Decimal(datos.get('precision_gps', ''))
    except (InvalidOperation, TypeError):
        raise ValueError('No se recibieron coordenadas GPS válidas.')
    if not -90 <= latitud <= 90 or not -180 <= longitud <= 180:
        raise ValueError('Las coordenadas GPS están fuera de rango.')
    if precision < 0:
        raise ValueError('La precisión GPS no puede ser negativa.')
    return latitud, longitud, precision


def decodificar_firma(valor, nombre):
    if not valor or not valor.startswith('data:image/png;base64,'):
        raise ValueError(f'Debe registrar la firma de {"el instructor" if nombre == "firma_instructor" else "el docente enlace"}.')
    try:
        contenido = base64.b64decode(valor.split(',', 1)[1], validate=True)
    except (ValueError, binascii.Error):
        raise ValueError('Una de las firmas no tiene un formato válido.')
    if len(contenido) > 512 * 1024:
        raise ValueError('La imagen de firma no puede superar 512 KB.')
    return f'{nombre}.png', ContentFile(contenido)


@login_required
def detalle_seguimiento(request, pk):
    """
    Vista detallada de una bitácora de seguimiento, compromisos y acta adjunta.
    """
    bitacora = get_object_or_404(BitacoraSeguimiento.objects.select_related('ficha', 'ficha__institucion', 'instructor', 'matricula__aprendiz'), pk=pk)
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '').strip()
        if mensaje:
            MensajeSeguimiento.objects.create(
                bitacora=bitacora,
                remitente=request.user,
                mensaje=mensaje,
            )
            messages.success(request, 'Mensaje agregado al seguimiento.')
        return redirect('seguimiento_detalle', pk=bitacora.pk)
    hoy = timezone.localdate()
    estado_compromiso = (
        'vencido' if bitacora.compromisos and bitacora.fecha_verificacion and bitacora.fecha_verificacion < hoy
        else 'por_vencer' if bitacora.compromisos and bitacora.fecha_verificacion
        else 'sin_compromiso'
    )
    mapa_url = None
    google_maps_url = None
    if bitacora.latitud is not None and bitacora.longitud is not None:
        margen = Decimal('0.005')
        oeste = bitacora.longitud - margen
        este = bitacora.longitud + margen
        sur = bitacora.latitud - margen
        norte = bitacora.latitud + margen
        mapa_url = (
            'https://www.openstreetmap.org/export/embed.html?layer=mapnik'
            f'&marker={bitacora.latitud}%2C{bitacora.longitud}'
            f'&bbox={oeste}%2C{sur}%2C{este}%2C{norte}'
        )
        google_maps_url = f'https://www.google.com/maps/search/?api=1&query={bitacora.latitud},{bitacora.longitud}'
    return render(request, 'seguimiento/detalle.html', {
        'bitacora': bitacora,
        'estado_compromiso': estado_compromiso,
        'mapa_url': mapa_url,
        'google_maps_url': google_maps_url,
    })


@login_required
def descargar_acta_pdf(request, pk):
    bitacora = get_object_or_404(
        BitacoraSeguimiento.objects.select_related('ficha__institucion', 'instructor', 'matricula__aprendiz'),
        pk=pk,
    )
    institucion = bitacora.ficha.institucion
    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    estilos = getSampleStyleSheet()
    titulo_entidad = ParagraphStyle('EntidadActa', parent=estilos['Normal'], alignment=TA_CENTER, fontSize=11, leading=14, textColor=colors.HexColor('#04324D'), fontName='Helvetica-Bold')
    subtitulo_sinetec = ParagraphStyle('SubSinetec', parent=estilos['Normal'], alignment=TA_CENTER, fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'))
    titulo_acta = ParagraphStyle('TituloActa', parent=estilos['Title'], alignment=TA_CENTER, fontSize=13, leading=16, textColor=colors.HexColor('#29AAE3'), fontName='Helvetica-Bold')
    texto = ParagraphStyle('TextoActa', parent=estilos['BodyText'], fontSize=9, leading=12)

    logo_sena_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'sena_logo_oficial.png')
    if os.path.exists(logo_sena_path):
        logo_flowable = PDFImage(logo_sena_path, width=0.9 * inch, height=0.9 * inch)
        header_table = Table([
            [logo_flowable, [
                Paragraph('SERVICIO NACIONAL DE APRENDIZAJE · SENA', titulo_entidad),
                Paragraph('SINETEC · SISTEMA INTEGRADO DE MEDIA TÉCNICA', subtitulo_sinetec),
                Paragraph('ACTA OFICIAL DE VISITA Y SEGUIMIENTO EN AULA', titulo_acta),
            ]]
        ], colWidths=[1.1 * inch, 6.1 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        contenido = [header_table, Spacer(1, 10)]
    else:
        contenido = [
            Paragraph('SERVICIO NACIONAL DE APRENDIZAJE · SENA', titulo_entidad),
            Paragraph('SINETEC · SISTEMA INTEGRADO DE MEDIA TÉCNICA', subtitulo_sinetec),
            Paragraph('ACTA OFICIAL DE VISITA Y SEGUIMIENTO EN AULA', titulo_acta),
            Spacer(1, 10),
        ]

    datos = [
        ['Institución articulada', institucion.nombre],
        ['Municipio / Sede', institucion.municipio],
        ['Ficha técnica', bitacora.ficha.codigo_ficha],
        ['Programa de formación', bitacora.ficha.programa.denominacion],
        ['Fecha de visita', bitacora.fecha_visita.strftime('%d/%m/%Y')],
        ['Tipo de sesión', bitacora.get_tipo_seguimiento_display()],
        ['Destinatario', bitacora.matricula.aprendiz.get_full_name() if bitacora.matricula else 'Acompañamiento general de la ficha técnica'],
    ]
    tabla_datos = Table(datos, colWidths=[1.75 * inch, 5.45 * inch])
    tabla_datos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0FDF4')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#166534')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    contenido.append(tabla_datos)
    contenido.extend([
        Spacer(1, 14),
        Paragraph('<b>Diagnóstico y observaciones pedagógicas/técnicas</b>', estilos['Heading3']),
        Paragraph(bitacora.observaciones.replace('\n', '<br/>'), texto),
    ])
    if bitacora.compromisos:
        contenido.extend([
            Spacer(1, 12),
            Paragraph('<b>Compromisos y plan de mejora (RN-006)</b>', estilos['Heading3']),
            Paragraph(bitacora.compromisos.replace('\n', '<br/>'), texto),
            Paragraph(f'<b>Fecha límite de verificación:</b> {bitacora.fecha_verificacion:%d/%m/%Y}', texto),
        ])
    firma_instructor = PDFImage(bitacora.firma_instructor.path, width=2.2 * inch, height=0.65 * inch, preserveAspectRatio=True) if bitacora.firma_instructor and os.path.exists(bitacora.firma_instructor.path) else Paragraph('______________________________', texto)
    firma_docente = PDFImage(bitacora.firma_docente_enlace.path, width=2.2 * inch, height=0.65 * inch, preserveAspectRatio=True) if bitacora.firma_docente_enlace and os.path.exists(bitacora.firma_docente_enlace.path) else Paragraph('______________________________', texto)
    contenido.extend([
        Spacer(1, 36),
        Table([
            [firma_instructor, firma_docente],
            [bitacora.instructor.get_full_name() or bitacora.instructor.username, institucion.enlace_nombre or 'Docente enlace'],
            ['Instructor SENA', 'Docente enlace de la institución'],
        ], colWidths=[3.6 * inch, 3.6 * inch], style=TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('TOPPADDING', (0, 1), (-1, 1), 4),
        ])),
        Spacer(1, 16),
        Paragraph('Documento oficial generado por la plataforma SINETEC - Articulación con la Media Técnica SENA.', texto),
    ])
    documento.build(contenido)
    respuesta = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    respuesta['Content-Disposition'] = f'attachment; filename="acta_visita_{bitacora.pk}.pdf"'
    return respuesta


@login_required
def editar_seguimiento(request, pk):
    """
    Edición administrativa de una bitácora de seguimiento formativo.
    """
    bitacora = get_object_or_404(BitacoraSeguimiento, pk=pk)
    if request.method == 'POST':
        form = BitacoraSeguimientoForm(request.POST, request.FILES, instance=bitacora)
        if form.is_valid():
            bitacora = form.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Seguimiento',
                accion='Modificación',
                detalles=f"Actualizó la bitácora #{bitacora.id} (Ficha {bitacora.ficha.codigo_ficha})",
                request=request
            )
            messages.success(request, f"Bitácora de seguimiento #{bitacora.id} actualizada correctamente.")
            return redirect('seguimiento_detalle', pk=bitacora.pk)
        else:
            messages.error(request, "Por favor revise los campos del formulario. Si registró compromisos, debe indicar fecha límite (RN-006).")
    else:
        form = BitacoraSeguimientoForm(instance=bitacora)

    return render(request, 'seguimiento/formulario.html', {
        'form': form,
        'titulo': f'Editar Bitácora de Seguimiento #{bitacora.id}',
        'bitacora': bitacora,
        'es_edicion': True,
    })


@login_required
def cambiar_estado_seguimiento(request, pk):
    """
    Cambio ágil del estado de la bitácora (Pendiente, En Proceso, Realizado).
    """
    bitacora = get_object_or_404(BitacoraSeguimiento, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado', '').strip()
        estados_validos = [e[0] for e in BitacoraSeguimiento.ESTADOS_SEGUIMIENTO]
        if nuevo_estado in estados_validos:
            antiguo = bitacora.estado
            bitacora.estado = nuevo_estado
            bitacora.save(update_fields=['estado'])
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Seguimiento',
                accion='Modificación',
                detalles=f"Cambió estado de bitácora #{bitacora.id} de '{antiguo}' a '{nuevo_estado}'",
                request=request
            )
            messages.success(request, f"Estado del seguimiento actualizado a '{nuevo_estado}'.")
        else:
            messages.error(request, "Estado no válido.")
    return redirect(request.META.get('HTTP_REFERER') or f'/seguimiento/{bitacora.pk}/')


@login_required
def eliminar_seguimiento(request, pk):
    """
    Eliminación protegida de una bitácora de seguimiento con registro en auditoría.
    """
    bitacora = get_object_or_404(BitacoraSeguimiento, pk=pk)
    if request.method == 'POST':
        bitacora_id = bitacora.id
        ficha_codigo = bitacora.ficha.codigo_ficha
        bitacora.delete()
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Seguimiento',
            accion='Eliminación',
            detalles=f"Eliminó la bitácora #{bitacora_id} de la ficha {ficha_codigo}",
            request=request
        )
        messages.success(request, f"La bitácora de seguimiento #{bitacora_id} ha sido eliminada del sistema.")
        return redirect('seguimiento_lista')
    return render(request, 'seguimiento/confirmar_eliminar_seguimiento.html', {'bitacora': bitacora})


@login_required
def subir_evidencia_seguimiento(request, pk):
    """
    Carga ágil de evidencia documental o soporte escaneado directamente desde la ficha de detalle.
    """
    bitacora = get_object_or_404(BitacoraSeguimiento, pk=pk)
    if request.method == 'POST' and request.FILES.get('archivo_adjunto'):
        archivo = request.FILES['archivo_adjunto']
        bitacora.archivo_adjunto = archivo
        bitacora.save(update_fields=['archivo_adjunto'])
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Seguimiento',
            accion='Subida Evidencia',
            detalles=f"Adjuntó evidencia a bitácora #{bitacora.id}: {archivo.name}",
            request=request
        )
        messages.success(request, f"Evidencia documental '{archivo.name}' cargada con éxito.")
    else:
        messages.error(request, "Debe seleccionar un archivo válido para adjuntar.")
    return redirect('seguimiento_detalle', pk=bitacora.pk)


@login_required
def eliminar_evidencia_seguimiento(request, pk):
    """
    Eliminación del archivo de evidencia adjunto en una bitácora.
    """
    bitacora = get_object_or_404(BitacoraSeguimiento, pk=pk)
    if request.method == 'POST':
        if bitacora.archivo_adjunto:
            nombre = bitacora.archivo_adjunto.name
            bitacora.archivo_adjunto.delete(save=False)
            bitacora.archivo_adjunto = None
            bitacora.save(update_fields=['archivo_adjunto'])
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Seguimiento',
                accion='Eliminación Evidencia',
                detalles=f"Eliminó evidencia de bitácora #{bitacora.id}: {nombre}",
                request=request
            )
            messages.success(request, "Evidencia documental eliminada de la bitácora.")
        else:
            messages.info(request, "La bitácora no tiene ningún documento adjunto.")
    return redirect('seguimiento_detalle', pk=bitacora.pk)


@login_required
def secretaria_bandeja(request):
    """
    Bandeja de gestión de solicitudes y trámites ante la Secretaría del SENA.
    """
    estado_filtro = request.GET.get('estado', '').strip()
    categoria_filtro = request.GET.get('categoria', '').strip()
    query = request.GET.get('q', '').strip()

    solicitudes = SolicitudSecretaria.objects.select_related(
        'aprendiz', 'aprendiz__perfil', 'ficha', 'responsable'
    ).all()

    if estado_filtro:
        solicitudes = solicitudes.filter(estado=estado_filtro)
    if categoria_filtro:
        solicitudes = solicitudes.filter(categoria=categoria_filtro)
    if query:
        solicitudes = solicitudes.filter(
            Q(asunto__icontains=query) |
            Q(mensaje__icontains=query) |
            Q(aprendiz__first_name__icontains=query) |
            Q(aprendiz__last_name__icontains=query) |
            Q(aprendiz__perfil__numero_documento__icontains=query)
        )

    context = {
        'solicitudes': solicitudes,
        'query': query,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'total_solicitudes': SolicitudSecretaria.objects.count(),
        'pendientes': SolicitudSecretaria.objects.filter(estado__in=['ENVIADA', 'RECIBIDA', 'EN_REVISION']).count(),
        'respondidas': SolicitudSecretaria.objects.filter(estado='RESPONDIDA').count(),
        'cerradas': SolicitudSecretaria.objects.filter(estado='CERRADA').count(),
        'categorias': SolicitudSecretaria.CATEGORIAS_SOLICITUD,
        'estados': SolicitudSecretaria.ESTADOS_SOLICITUD,
    }
    return render(request, 'seguimiento/secretaria_bandeja.html', context)


@login_required
def nueva_solicitud(request):
    """
    Formulario oficial 'CONTACTAR SECRETARÍA' para que aprendices e instructores
    radiquen una nueva solicitud, trámite o novedad ante la Secretaría SENA.
    """
    fichas = Ficha.objects.all()
    perfil = getattr(request.user, 'perfil', None)
    ficha_defecto = None
    if perfil and perfil.rol and perfil.rol.nombre == 'Estudiante':
        mat = Matricula.objects.filter(aprendiz=request.user).first()
        if mat:
            ficha_defecto = mat.ficha

    if request.method == 'POST':
        asunto = request.POST.get('asunto', '').strip()
        categoria = request.POST.get('categoria', 'Academica')
        prioridad = request.POST.get('prioridad', 'Media')
        mensaje = request.POST.get('mensaje', '').strip()
        ficha_id = request.POST.get('ficha_id')
        archivo = request.FILES.get('archivo_adjunto')

        if not asunto or not mensaje:
            messages.error(request, "Por favor complete el asunto y la descripción detallada del trámite.")
        else:
            ficha_asociada = Ficha.objects.filter(id=ficha_id).first() if ficha_id else ficha_defecto
            solicitud = SolicitudSecretaria.objects.create(
                aprendiz=request.user,
                ficha=ficha_asociada,
                asunto=asunto,
                categoria=categoria,
                prioridad=prioridad,
                mensaje=mensaje,
                archivo_adjunto=archivo,
                estado='ENVIADA',
            )

            # Notificar a coordinadores/secretaría
            responsables = User.objects.filter(perfil__rol__nombre__in=['Coordinador', 'Administrador'])
            for resp in responsables:
                Notificacion.objects.create(
                    usuario=resp,
                    titulo=f"Nueva solicitud de {request.user.get_full_name() or request.user.username}",
                    mensaje=f"[{solicitud.get_categoria_display()}] {solicitud.asunto}",
                    enlace=f"/seguimiento/secretaria/solicitud/{solicitud.id}/",
                    tipo='info'
                )

            # Auditoría
            RegistroAuditoria.objects.create(
                usuario=request.user,
                accion="Radicación de solicitud a Secretaría",
                modulo="Secretaría",
                detalles=f"Solicitud #{solicitud.id} - {solicitud.asunto} ({solicitud.categoria})"
            )

            messages.success(request, "¡Tu solicitud ha sido radicada formalmente ante la Secretaría SENA! Te notificaremos cuando haya respuesta.")
            return redirect('mis_solicitudes')

    return render(request, 'seguimiento/secretaria_nueva.html', {
        'fichas': fichas,
        'ficha_defecto': ficha_defecto,
        'categorias': SolicitudSecretaria.CATEGORIAS_SOLICITUD,
        'prioridades': SolicitudSecretaria.PRIORIDADES_SOLICITUD,
    })


@login_required
def mis_solicitudes(request):
    """
    Consulta de las solicitudes radicadas por el usuario actual.
    """
    solicitudes = SolicitudSecretaria.objects.filter(aprendiz=request.user).select_related('ficha', 'responsable').order_by('-fecha_creacion')
    return render(request, 'seguimiento/mis_solicitudes.html', {
        'solicitudes': solicitudes,
        'total': solicitudes.count(),
    })


@login_required
def secretaria_detalle(request, pk):
    """
    Expediente de una solicitud ante Secretaría: conversación, respuesta oficial,
    adjuntos y cambio de estado del trámite.
    """
    solicitud = get_object_or_404(
        SolicitudSecretaria.objects.select_related('aprendiz', 'aprendiz__perfil', 'ficha', 'responsable'),
        pk=pk
    )

    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    es_personal = request.user.is_superuser or rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA']

    if not es_personal and solicitud.aprendiz != request.user:
        messages.error(request, "No tienes permisos para consultar esta solicitud.")
        return redirect('mis_solicitudes')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'responder':
            texto_resp = request.POST.get('mensaje', '').strip()
            archivo_resp = request.FILES.get('archivo_adjunto')
            if texto_resp:
                RespuestaSolicitud.objects.create(
                    solicitud=solicitud,
                    usuario=request.user,
                    mensaje=texto_resp,
                    archivo_adjunto=archivo_resp
                )

                if es_personal:
                    solicitud.estado = 'RESPONDIDA'
                    solicitud.responsable = request.user
                    solicitud.save(update_fields=['estado', 'responsable', 'fecha_actualizacion'])

                    Notificacion.objects.create(
                        usuario=solicitud.aprendiz,
                        titulo="Secretaría respondió tu solicitud",
                        mensaje=f"Hay una respuesta oficial a tu trámite: '{solicitud.asunto}'",
                        enlace=f"/seguimiento/secretaria/solicitud/{solicitud.id}/",
                        tipo='success'
                    )
                else:
                    solicitud.estado = 'EN_REVISION'
                    solicitud.save(update_fields=['estado', 'fecha_actualizacion'])

                messages.success(request, "Respuesta enviada y registrada en el expediente.")
                return redirect('secretaria_detalle', pk=solicitud.pk)

        elif accion == 'cambiar_estado' and es_personal:
            nuevo_estado = request.POST.get('nuevo_estado')
            if nuevo_estado in dict(SolicitudSecretaria.ESTADOS_SOLICITUD):
                solicitud.estado = nuevo_estado
                solicitud.responsable = request.user
                solicitud.save(update_fields=['estado', 'responsable', 'fecha_actualizacion'])

                RegistroAuditoria.objects.create(
                    usuario=request.user,
                    accion=f"Cambio de estado a {nuevo_estado} en solicitud #{solicitud.id}",
                    modulo="Secretaría",
                    detalles=f"Solicitud: {solicitud.asunto}"
                )

                messages.success(request, f"Estado actualizado a: {solicitud.get_estado_display()}")
                return redirect('secretaria_detalle', pk=solicitud.pk)

    respuestas = solicitud.respuestas.select_related('usuario', 'usuario__perfil').order_by('fecha_respuesta')
    return render(request, 'seguimiento/secretaria_detalle.html', {
        'solicitud': solicitud,
        'respuestas': respuestas,
        'es_personal': es_personal,
        'estados': SolicitudSecretaria.ESTADOS_SOLICITUD,
    })


@login_required
def cambiar_estado_solicitud(request, pk):
    """Acción rápida para cambiar el estado de una solicitud."""
    if request.method == 'POST':
        return secretaria_detalle(request, pk)
    return redirect('secretaria_bandeja')


@login_required
def proyectar_qr_sesion(request, ficha_id):
    """
    Proyector en pantalla grande / aula del Código QR dinámico de asistencia diaria.
    El QR rota diariamente (cada 24 horas) para garantizar presencia física en el aula.
    """
    import hashlib
    import qrcode
    from django.conf import settings

    ficha = get_object_or_404(Ficha.objects.select_related('programa', 'institucion', 'instructor_lider'), pk=ficha_id)
    hoy = timezone.localdate()
    ahora = timezone.localtime()

    # Generar token criptográfico único para el día de hoy
    seed = f"SINETEC-SESION-{ficha.codigo_ficha}-{hoy}-{settings.SECRET_KEY}"
    token_hoy = hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16]

    url_marcado = request.build_absolute_uri(
        f'/seguimiento/asistencia/marcar-sesion/{ficha.id}/?fecha={hoy}&token={token_hoy}'
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url_marcado)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#002233", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

    total_matriculados = ficha.matriculas.filter(estado_formacion='En Formacion').count()
    asistencias_hoy = AsistenciaAprendiz.objects.filter(matricula__ficha=ficha, fecha=hoy, estado='P').count()

    return render(request, 'seguimiento/proyectar_qr_sesion.html', {
        'ficha': ficha,
        'hoy': hoy,
        'ahora': ahora,
        'token_hoy': token_hoy,
        'url_marcado': url_marcado,
        'qr_base64': qr_base64,
        'total_matriculados': total_matriculados,
        'asistencias_hoy': asistencias_hoy,
    })


def marcar_asistencia_sesion(request, ficha_id):
    """
    Página de confirmación y registro cuando un aprendiz escanea el código QR proyectado en clase.
    Valida rigurosamente la fecha de hoy y el token criptográfico diario.
    """
    import hashlib
    from django.conf import settings

    ficha = get_object_or_404(Ficha.objects.select_related('programa', 'institucion'), pk=ficha_id)
    hoy = timezone.localdate()
    ahora = timezone.localtime()

    fecha_param = request.GET.get('fecha') or request.POST.get('fecha')
    token_param = request.GET.get('token') or request.POST.get('token')

    # Validar fecha: no se permiten fotos o capturas de ayer
    if fecha_param and fecha_param != str(hoy):
        return render(request, 'usuarios/qr_invalido.html', {
            'mensaje': f'El código QR de sesión escaneado pertenece a la fecha {fecha_param} y ya no tiene validez. El código QR del aula rota todos los días por seguridad institucional SENA.',
            'hoy': hoy,
        }, status=410)

    # Validar token criptográfico del día
    seed = f"SINETEC-SESION-{ficha.codigo_ficha}-{hoy}-{settings.SECRET_KEY}"
    token_esperado = hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16]
    if token_param != token_esperado:
        return render(request, 'usuarios/qr_invalido.html', {
            'mensaje': 'El código de seguridad del QR de clase no coincide o ha caducado.',
            'hoy': hoy,
        }, status=400)

    aprendiz_user = None
    if request.user.is_authenticated:
        aprendiz_user = request.user
    elif request.method == 'POST':
        documento = request.POST.get('documento', '').strip()
        from usuarios.models import PerfilUsuario
        perfil = PerfilUsuario.objects.filter(
            Q(numero_documento=documento) | Q(usuario__username=documento)
        ).first()
        if perfil:
            aprendiz_user = perfil.usuario
        else:
            messages.error(request, f'No se encontró ningún aprendiz asociado al documento "{documento}".')

    if aprendiz_user:
        matricula = Matricula.objects.filter(ficha=ficha, aprendiz=aprendiz_user).first()
        if not matricula:
            return render(request, 'usuarios/qr_invalido.html', {
                'mensaje': f'El aprendiz {aprendiz_user.get_full_name() or aprendiz_user.username} no está matriculado formalmente en la Ficha {ficha.codigo_ficha}.',
                'hoy': hoy,
            }, status=403)

        asistencia, creado = AsistenciaAprendiz.objects.get_or_create(
            matricula=matricula,
            fecha=hoy,
            defaults={
                'estado': 'P',
                'observaciones': 'Asistencia a clase registrada mediante escaneo de QR proyectado en aula',
                'registrado_por': aprendiz_user,
            }
        )
        if not creado and asistencia.estado != 'P':
            asistencia.estado = 'P'
            asistencia.observaciones = 'Asistencia actualizada a Presente por QR de sesión'
            asistencia.save(update_fields=['estado', 'observaciones'])

        return render(request, 'seguimiento/sesion_asistencia_confirmada.html', {
            'ficha': ficha,
            'matricula': matricula,
            'asistencia': asistencia,
            'hoy': hoy,
            'ahora': ahora,
            'creado': creado,
        })

    # Si no está autenticado y no envió POST, mostrar formulario rápido para ingresar documento
    return render(request, 'seguimiento/sesion_marcar_form.html', {
        'ficha': ficha,
        'hoy': hoy,
        'fecha_param': fecha_param,
        'token_param': token_param,
    })


# ==============================================================================
# MÓDULO 1: SEGUIMIENTOS ADMINISTRATIVOS E INTERINSTITUCIONALES
# ==============================================================================

@login_required
def seguimientos_administrativos_lista(request):
    """
    Directorio integral de seguimientos y compromisos administrativos
    entre el SENA y las Instituciones Educativas articuladas.
    """
    query = request.GET.get('q', '').strip()
    colegio_filtro = request.GET.get('colegio', '').strip()
    prioridad_filtro = request.GET.get('prioridad', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    seguimientos = SeguimientoAdministrativo.objects.select_related(
        'institucion', 'convenio', 'responsable'
    ).order_by('-fecha_limite', '-fecha_registro')

    if query:
        seguimientos = seguimientos.filter(
            Q(asunto__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(resultado__icontains=query) |
            Q(institucion__nombre__icontains=query)
        )

    if colegio_filtro:
        seguimientos = seguimientos.filter(institucion_id=colegio_filtro)

    if prioridad_filtro:
        seguimientos = seguimientos.filter(prioridad=prioridad_filtro)

    if estado_filtro:
        seguimientos = seguimientos.filter(estado=estado_filtro)

    # Indicadores KPIs
    hoy = timezone.localdate()
    total_seguimientos = SeguimientoAdministrativo.objects.count()
    total_pendientes = SeguimientoAdministrativo.objects.filter(estado='Pendiente').count()
    total_en_proceso = SeguimientoAdministrativo.objects.filter(estado='En Proceso').count()
    total_atrasados = SeguimientoAdministrativo.objects.filter(
        fecha_limite__lt=hoy
    ).exclude(estado__in=['Completado', 'Cancelado']).count()

    paginator = Paginator(seguimientos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    colegios = InstitucionEducativa.objects.order_by('nombre')
    prioridades = SeguimientoAdministrativo.PRIORIDAD_CHOICES
    estados = SeguimientoAdministrativo.ESTADO_CHOICES

    context = {
        'page_obj': page_obj,
        'seguimientos': page_obj,
        'total_seguimientos': total_seguimientos,
        'total_pendientes': total_pendientes,
        'total_en_proceso': total_en_proceso,
        'total_atrasados': total_atrasados,
        'colegios': colegios,
        'prioridades': prioridades,
        'estados': estados,
        'query': query,
        'colegio_filtro': colegio_filtro,
        'prioridad_filtro': prioridad_filtro,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'seguimiento/seguimientos_admin_lista.html', context)


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría', 'Instructor SENA')
def seguimiento_admin_crear(request):
    """
    Crear un nuevo seguimiento o tarea administrativa para un colegio/convenio.
    """
    institucion_previa = request.GET.get('institucion')
    if request.method == 'POST':
        form = SeguimientoAdministrativoForm(request.POST)
        if form.is_valid():
            seg = form.save(commit=False)
            seg.responsable = request.user
            seg.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Seguimientos',
                accion='Creación de Seguimiento',
                detalles=f"Se creó el seguimiento administrativo '{seg.asunto}' ({seg.prioridad}) para {seg.institucion.nombre}.",
                request=request
            )
            messages.success(request, f"Seguimiento '{seg.asunto}' registrado con éxito.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('seguimientos_admin_lista')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        initial = {'institucion': institucion_previa, 'fecha': timezone.localdate()}
        form = SeguimientoAdministrativoForm(initial=initial)

    return render(request, 'seguimiento/seguimiento_admin_formulario.html', {
        'form': form,
        'titulo': 'Nuevo Seguimiento Administrativo'
    })


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría', 'Instructor SENA')
def seguimiento_admin_editar(request, pk):
    """
    Edición de un seguimiento administrativo existente.
    """
    seg = get_object_or_404(SeguimientoAdministrativo, pk=pk)
    if request.method == 'POST':
        form = SeguimientoAdministrativoForm(request.POST, instance=seg)
        if form.is_valid():
            seg = form.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Seguimientos',
                accion='Edición de Seguimiento',
                detalles=f"Se actualizó seguimiento '{seg.asunto}' de {seg.institucion.nombre}.",
                request=request
            )
            messages.success(request, f"Seguimiento '{seg.asunto}' actualizado exitosamente.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('seguimientos_admin_lista')
        else:
            messages.error(request, "Por favor revise los campos señalados.")
    else:
        form = SeguimientoAdministrativoForm(instance=seg)

    return render(request, 'seguimiento/seguimiento_admin_formulario.html', {
        'form': form,
        'titulo': 'Editar Seguimiento Administrativo',
        'seguimiento': seg
    })


@login_required
def seguimiento_admin_cambiar_estado(request, pk):
    """
    Cambio rápido de estado para un seguimiento administrativo.
    """
    seg = get_object_or_404(SeguimientoAdministrativo, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado', 'Completado')
        seg.estado = nuevo_estado
        seg.save(update_fields=['estado'])
        messages.success(request, f"Seguimiento '{seg.asunto}' actualizado a '{nuevo_estado}'.")
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('seguimientos_admin_lista')


@login_required
@requerir_roles('Administrador', 'Coordinador')
def seguimiento_admin_eliminar(request, pk):
    """
    Eliminación segura de un seguimiento administrativo.
    """
    seg = get_object_or_404(SeguimientoAdministrativo, pk=pk)
    if request.method == 'POST':
        asunto = seg.asunto
        col = seg.institucion.nombre
        seg.delete()
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Seguimientos',
            accion='Eliminación de Seguimiento',
            detalles=f"Se eliminó el seguimiento '{asunto}' de la institución {col}.",
            request=request
        )
        messages.success(request, f"Seguimiento '{asunto}' eliminado correctamente.")
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('seguimientos_admin_lista')

    return render(request, 'seguimiento/confirmar_eliminar_seguimiento_admin.html', {'seguimiento': seg})


# ==============================================================================
# MÓDULO 2: CALENDARIO Y AGENDA ADMINISTRATIVA INSTITUCIONAL
# ==============================================================================

@login_required
def calendario_administrativo(request):
    """
    Agenda interactiva de eventos, reuniones, visitas y vencimientos de convenios.
    """
    hoy = timezone.localdate()
    tipo_filtro = request.GET.get('tipo', '').strip()
    colegio_filtro = request.GET.get('colegio', '').strip()

    eventos = EventoCalendario.objects.select_related(
        'institucion', 'convenio', 'responsable'
    ).order_by('fecha', 'hora')

    if tipo_filtro:
        eventos = eventos.filter(tipo_evento=tipo_filtro)
    if colegio_filtro:
        eventos = eventos.filter(institucion_id=colegio_filtro)

    # Indicadores
    eventos_proximos = eventos.filter(fecha__gte=hoy)[:20]
    total_eventos = EventoCalendario.objects.count()
    eventos_mes = EventoCalendario.objects.filter(fecha__year=hoy.year, fecha__month=hoy.month).count()
    reuniones_pendientes = EventoCalendario.objects.filter(tipo_evento='Reunión', fecha__gte=hoy).count()
    vencimientos_proximos = ConvenioSENA.objects.filter(
        fecha_fin__gte=hoy,
        fecha_fin__lte=hoy + timezone.timedelta(days=60)
    ).count()

    colegios = InstitucionEducativa.objects.order_by('nombre')
    tipos_evento = EventoCalendario.TIPO_CHOICES
    convenios_activos = ConvenioSENA.objects.filter(fecha_fin__gte=hoy).order_by('nombre')

    context = {
        'eventos': eventos_proximos,
        'hoy': hoy,
        'total_eventos': total_eventos,
        'eventos_mes': eventos_mes,
        'reuniones_pendientes': reuniones_pendientes,
        'vencimientos_proximos': vencimientos_proximos,
        'colegios': colegios,
        'tipos_evento': tipos_evento,
        'convenios_activos': convenios_activos,
        'tipo_filtro': tipo_filtro,
        'colegio_filtro': colegio_filtro,
    }
    return render(request, 'seguimiento/calendario.html', context)


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría', 'Instructor SENA')
def evento_calendario_crear(request):
    """
    Agendar un nuevo evento en el calendario administrativo.
    """
    if request.method == 'POST':
        form = EventoCalendarioForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.responsable = request.user
            ev.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Calendario',
                accion='Creación de Evento',
                detalles=f"Se agendó '{ev.titulo}' ({ev.tipo_evento}) para el {ev.fecha.strftime('%d/%m/%Y')}.",
                request=request
            )
            messages.success(request, f"Evento '{ev.titulo}' agendado exitosamente.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('calendario_administrativo')
        else:
            messages.error(request, "Por favor complete todos los datos obligatorios del evento.")
    else:
        initial = {'fecha': timezone.localdate()}
        form = EventoCalendarioForm(initial=initial)

    return render(request, 'seguimiento/evento_formulario.html', {
        'form': form,
        'titulo': 'Agendar Nuevo Evento'
    })


@login_required
@requerir_roles('Administrador', 'Coordinador')
def evento_calendario_eliminar(request, pk):
    """
    Eliminación de un evento del calendario.
    """
    ev = get_object_or_404(EventoCalendario, pk=pk)
    if request.method == 'POST':
        tit = ev.titulo
        ev.delete()
        messages.success(request, f"Evento '{tit}' retirado de la agenda.")
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('calendario_administrativo')

    return render(request, 'seguimiento/confirmar_eliminar_evento.html', {'evento': ev})


# ==============================================================================
# MÓDULO 3: BIBLIOTECA Y REPOSITORIO DOCUMENTAL ADMINISTRATIVO
# ==============================================================================

@login_required
def documentos_admin_lista(request):
    """
    Biblioteca documental digital: repositorio oficial de convenios, actas,
    resoluciones, cartas, pólizas y formatos oficiales SENA.
    """
    query = request.GET.get('q', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    colegio_filtro = request.GET.get('colegio', '').strip()
    convenio_filtro = request.GET.get('convenio', '').strip()

    documentos = DocumentoAdministrativo.objects.select_related(
        'institucion', 'convenio', 'programa', 'subido_por'
    ).order_by('-fecha_subida')

    if query:
        documentos = documentos.filter(
            Q(nombre__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(institucion__nombre__icontains=query) |
            Q(convenio__nombre__icontains=query)
        )

    if tipo_filtro:
        documentos = documentos.filter(tipo=tipo_filtro)

    if colegio_filtro:
        documentos = documentos.filter(institucion_id=colegio_filtro)

    if convenio_filtro:
        documentos = documentos.filter(convenio_id=convenio_filtro)

    # Indicadores
    total_documentos = DocumentoAdministrativo.objects.count()
    total_convenios = DocumentoAdministrativo.objects.filter(tipo='Convenio').count()
    total_actas = DocumentoAdministrativo.objects.filter(tipo='Acta').count()
    total_resoluciones = DocumentoAdministrativo.objects.filter(tipo='Resolución').count()

    paginator = Paginator(documentos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    colegios = InstitucionEducativa.objects.order_by('nombre')
    convenios = ConvenioSENA.objects.order_by('nombre')
    tipos_doc = DocumentoAdministrativo.TIPO_CHOICES

    context = {
        'page_obj': page_obj,
        'documentos': page_obj,
        'total_documentos': total_documentos,
        'total_convenios': total_convenios,
        'total_actas': total_actas,
        'total_resoluciones': total_resoluciones,
        'colegios': colegios,
        'convenios': convenios,
        'tipos_doc': tipos_doc,
        'query': query,
        'tipo_filtro': tipo_filtro,
        'colegio_filtro': colegio_filtro,
        'convenio_filtro': convenio_filtro,
    }
    return render(request, 'seguimiento/documentos_admin_lista.html', context)


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría', 'Instructor SENA')
def documento_admin_subir(request):
    """
    Subida formal de un nuevo documento al repositorio administrativo.
    """
    if request.method == 'POST':
        form = DocumentoAdministrativoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.subido_por = request.user
            doc.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Documentos',
                accion='Carga de Documento',
                detalles=f"Se cargó documento '{doc.nombre}' ({doc.tipo}) al repositorio.",
                request=request
            )
            messages.success(request, f"Documento '{doc.nombre}' almacenado exitosamente.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('documentos_admin_lista')
        else:
            messages.error(request, "Por favor corrija los datos y seleccione un archivo válido.")
    else:
        initial = {'fecha_documento': timezone.localdate()}
        form = DocumentoAdministrativoForm(initial=initial)

    return render(request, 'seguimiento/documento_admin_formulario.html', {
        'form': form,
        'titulo': 'Subir Documento Administrativo'
    })


@login_required
def documento_admin_descargar(request, pk):
    """
    Descarga real y protegida del archivo digital desde el repositorio.
    """
    doc = get_object_or_404(DocumentoAdministrativo, pk=pk)
    if not doc.archivo or not os.path.exists(doc.archivo.path):
        messages.error(request, "El archivo solicitado no se encuentra disponible físicamente en el servidor.")
        return redirect('documentos_admin_lista')

    RegistroAuditoria.registrar(
        usuario=request.user,
        modulo='Documentos',
        accion='Descarga de Documento',
        detalles=f"Descarga de '{doc.nombre}' ({doc.archivo.name}).",
        request=request
    )
    return FileResponse(open(doc.archivo.path, 'rb'), as_attachment=True, filename=os.path.basename(doc.archivo.name))


@login_required
@requerir_roles('Administrador', 'Coordinador')
def documento_admin_eliminar(request, pk):
    """
    Eliminación segura de un documento del repositorio.
    """
    doc = get_object_or_404(DocumentoAdministrativo, pk=pk)
    if request.method == 'POST':
        nombre = doc.nombre
        if doc.archivo and os.path.exists(doc.archivo.path):
            try:
                os.remove(doc.archivo.path)
            except Exception:
                pass
        doc.delete()
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Documentos',
            accion='Eliminación de Documento',
            detalles=f"Se eliminó el documento '{nombre}' del repositorio digital.",
            request=request
        )
        messages.success(request, f"Documento '{nombre}' retirado del sistema.")
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('documentos_admin_lista')

    return render(request, 'seguimiento/confirmar_eliminar_documento.html', {'documento': doc})


