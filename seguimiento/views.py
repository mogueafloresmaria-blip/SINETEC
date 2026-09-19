from datetime import date
import base64
import binascii
import os
from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.core.files.base import ContentFile
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from django.db.models import Q
from reportlab.platypus import Image as PDFImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from .models import AsistenciaAprendiz, BitacoraSeguimiento, MensajeSeguimiento, SolicitudSecretaria, RespuestaSolicitud, Notificacion, RegistroAuditoria
from .forms import BitacoraSeguimientoForm
from academico.models import Ficha, Matricula
from django.contrib.auth.models import User


@login_required
def lista_seguimientos(request):
    """
    Historial general de bitácoras de visitas técnicas y acompañamiento.
    """
    ficha_id = request.GET.get('ficha', '').strip()
    seguimientos = BitacoraSeguimiento.objects.select_related('ficha', 'ficha__institucion', 'instructor', 'matricula__aprendiz').all()

    if ficha_id:
        seguimientos = seguimientos.filter(ficha_id=ficha_id)

    fichas = Ficha.objects.all().order_by('codigo_ficha')

    hoy = timezone.localdate()
    seguimientos = [
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

    context = {
        'seguimientos': seguimientos,
        'fichas': fichas,
        'ficha_seleccionada': ficha_id,
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
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle('TituloActa', parent=estilos['Title'], alignment=TA_CENTER, fontSize=15, leading=18, textColor=colors.HexColor('#8F5360'))
    texto = ParagraphStyle('TextoActa', parent=estilos['BodyText'], fontSize=9, leading=12)
    contenido = [
        Paragraph('SINETEC', titulo),
        Paragraph('ACTA OFICIAL DE VISITA Y SEGUIMIENTO', titulo),
        Spacer(1, 12),
    ]
    datos = [
        ['Institución educativa', institucion.nombre],
        ['Municipio', institucion.municipio],
        ['Ficha técnica', bitacora.ficha.codigo_ficha],
        ['Programa', bitacora.ficha.programa.denominacion],
        ['Fecha de visita', bitacora.fecha_visita.strftime('%d/%m/%Y')],
        ['Tipo de sesión', bitacora.get_tipo_seguimiento_display()],
        ['Destinatario', bitacora.matricula.aprendiz.get_full_name() if bitacora.matricula else 'Acompañamiento general de la ficha'],
    ]
    tabla_datos = Table(datos, colWidths=[1.65 * inch, 5.8 * inch])
    tabla_datos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#FBECEF')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#67434C')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#EAD5D9')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    contenido.append(tabla_datos)
    contenido.extend([
        Spacer(1, 16),
        Paragraph('<b>Diagnóstico y observaciones pedagógicas/técnicas</b>', estilos['Heading3']),
        Paragraph(bitacora.observaciones.replace('\n', '<br/>'), texto),
    ])
    if bitacora.compromisos:
        contenido.extend([
            Spacer(1, 12),
            Paragraph('<b>Compromisos y plan de mejora (RN-006)</b>', estilos['Heading3']),
            Paragraph(bitacora.compromisos.replace('\n', '<br/>'), texto),
            Paragraph(f'<b>Fecha de verificación:</b> {bitacora.fecha_verificacion:%d/%m/%Y}', texto),
        ])
    firma_instructor = PDFImage(bitacora.firma_instructor.path, width=2.2 * inch, height=0.65 * inch, preserveAspectRatio=True) if bitacora.firma_instructor and os.path.exists(bitacora.firma_instructor.path) else Paragraph('______________________________', texto)
    firma_docente = PDFImage(bitacora.firma_docente_enlace.path, width=2.2 * inch, height=0.65 * inch, preserveAspectRatio=True) if bitacora.firma_docente_enlace and os.path.exists(bitacora.firma_docente_enlace.path) else Paragraph('______________________________', texto)
    contenido.extend([
        Spacer(1, 42),
        Table([
            [firma_instructor, firma_docente],
            [bitacora.instructor.get_full_name() or bitacora.instructor.username, institucion.enlace_nombre or 'Docente enlace'],
            ['Instructor SENA', 'Docente enlace de la institución'],
        ], colWidths=[3.5 * inch, 3.5 * inch], style=TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, 1), 4),
        ])),
        Spacer(1, 18),
        Paragraph('Documento generado por SINETEC para entrega a la institución educativa.', texto),
    ])
    documento.build(contenido)
    respuesta = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    respuesta['Content-Disposition'] = f'attachment; filename="acta_visita_{bitacora.pk}.pdf"'
    return respuesta


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

