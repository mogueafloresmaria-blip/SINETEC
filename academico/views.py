import csv
import io
import unicodedata
from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, Count
from django.db import transaction
from django.http import HttpResponse
from .models import Ficha, Matricula, ProgramaFormacion, Competencia, ResultadoAprendizaje, HorarioFicha
from openpyxl import load_workbook, Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .forms import FichaForm, MatriculaRapidaForm, ImportarAprendicesForm, HorarioFichaForm
from usuarios.models import PerfilUsuario, Rol
from seguimiento.models import BitacoraSeguimiento, SolicitudSecretaria, RegistroAuditoria
from evaluaciones.models import JuicioEvaluativo


ENCABEZADOS_IMPORTACION = {
    'tipo_documento': {'tipo_documento', 'tipo_documento_identidad', 'tipo_de_documento'},
    'numero_documento': {'numero_documento', 'numero_de_documento', 'documento'},
    'nombres': {'nombres', 'nombre', 'nombres_completos'},
    'apellidos': {'apellidos', 'apellido', 'apellidos_completos'},
    'correo': {'correo', 'correo_electronico', 'email'},
    'telefono': {'telefono', 'telefono_celular', 'celular'},
    'grado_escolar': {'grado_escolar', 'grado', 'curso'},
    'acudiente_nombre': {'acudiente_nombre', 'nombre_acudiente', 'padre_acudiente'},
    'acudiente_telefono': {'acudiente_telefono', 'telefono_acudiente'},
}


def normalizar_encabezado(valor):
    valor = unicodedata.normalize('NFKD', str(valor or ''))
    valor = ''.join(caracter for caracter in valor if not unicodedata.combining(caracter))
    return ''.join(caracter if caracter.isalnum() else '_' for caracter in valor.lower()).strip('_')


def leer_archivo_aprendices(archivo):
    extension = archivo.name.lower().rsplit('.', 1)[-1]
    if extension == 'xlsx':
        libro = load_workbook(archivo, read_only=True, data_only=True)
        filas = list(libro.active.iter_rows(values_only=True))
        if not filas:
            raise ValueError('El archivo no contiene filas.')
        encabezados = filas[0]
        registros = filas[1:]
    else:
        contenido = archivo.read()
        try:
            texto = contenido.decode('utf-8-sig')
        except UnicodeDecodeError:
            texto = contenido.decode('latin-1')
        try:
            delimitador = csv.Sniffer().sniff(texto[:2048], delimiters=',;\t').delimiter
        except csv.Error:
            delimitador = ','
        lector = csv.reader(io.StringIO(texto), delimiter=delimitador, strict=False)
        filas = list(lector)
        if not filas:
            raise ValueError('El archivo no contiene filas.')
        encabezados = filas[0]
        registros = filas[1:]

    encabezados_normalizados = [normalizar_encabezado(valor) for valor in encabezados]
    mapa_columnas = {}
    for indice, encabezado in enumerate(encabezados_normalizados):
        for campo, alias in ENCABEZADOS_IMPORTACION.items():
            if encabezado in alias:
                mapa_columnas[campo] = indice
                break

    campos_requeridos = {'tipo_documento', 'numero_documento', 'nombres', 'apellidos', 'correo', 'grado_escolar'}
    faltantes = campos_requeridos - mapa_columnas.keys()
    if faltantes:
        raise ValueError(f'Faltan columnas obligatorias: {", ".join(sorted(faltantes))}.')

    datos = []
    for numero_fila, fila in enumerate(registros, start=2):
        valores = {
            campo: str(fila[indice] if indice < len(fila) and fila[indice] is not None else '').strip()
            for campo, indice in mapa_columnas.items()
        }
        if not any(valores.values()):
            continue
        valores['_fila'] = numero_fila
        datos.append(valores)
    return datos


def validar_importacion_aprendices(registros):
    documentos_archivo = set()
    registros_validos = []
    errores = []
    for registro in registros:
        numero_fila = registro.pop('_fila')
        formulario = MatriculaRapidaForm(registro)
        if not formulario.is_valid():
            detalles = '; '.join(
                f'{campo}: {", ".join(errores_campo)}'
                for campo, errores_campo in formulario.errors.items()
            )
            errores.append(f'Fila {numero_fila}: {detalles}')
            continue
        datos = formulario.cleaned_data
        documento = datos['numero_documento'].strip()
        if documento in documentos_archivo:
            errores.append(f'Fila {numero_fila}: el documento {documento} está repetido en el archivo.')
            continue
        documentos_archivo.add(documento)
        datos['_fila'] = numero_fila
        registros_validos.append(datos)

    documentos_existentes = set(
        PerfilUsuario.objects.filter(numero_documento__in=documentos_archivo)
        .values_list('numero_documento', flat=True)
    )
    for registro in registros_validos[:]:
        if registro['numero_documento'] in documentos_existentes:
            errores.append(
                f"Fila {registro['_fila']}: ya existe un usuario con el documento {registro['numero_documento']}."
            )
            registros_validos.remove(registro)
        elif User.objects.filter(username=f"ap_{registro['numero_documento']}").exists():
            errores.append(
                f"Fila {registro['_fila']}: el nombre de usuario generado para el documento "
                f"{registro['numero_documento']} ya está ocupado."
            )
            registros_validos.remove(registro)
    return registros_validos, errores


def crear_matricula_desde_datos(ficha, datos, rol_estudiante):
    numero_documento = datos['numero_documento'].strip()
    user = User.objects.create_user(
        username=f"ap_{numero_documento}",
        email=datos['correo'],
        first_name=datos['nombres'],
        last_name=datos['apellidos'],
        password=f"Sena{numero_documento[:4]}*",
    )
    perfil = user.perfil
    perfil.rol = rol_estudiante
    perfil.tipo_documento = datos['tipo_documento']
    perfil.numero_documento = numero_documento
    perfil.telefono = datos['telefono']
    perfil.save()
    return Matricula.objects.create(
        ficha=ficha,
        aprendiz=user,
        grado_escolar=datos['grado_escolar'],
        acudiente_nombre=datos['acudiente_nombre'],
        acudiente_telefono=datos['acudiente_telefono'],
    )


@login_required
def lista_fichas(request):
    """
    Listado general de Fichas de Media Técnica con filtros avanzados,
    búsqueda por número de ficha (3173430), programa, regional y estado.
    """
    query = request.GET.get('q', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    instructor_filtro = request.GET.get('instructor', '').strip()

    fichas = Ficha.objects.select_related(
        'programa', 'institucion', 'instructor_lider'
    ).annotate(
        num_aprendices=Count('matriculas', distinct=True),
        num_horarios=Count('horarios', distinct=True)
    ).all().order_by('-fecha_inicio')

    if query:
        fichas = fichas.filter(
            Q(codigo_ficha__icontains=query) |
            Q(programa__denominacion__icontains=query) |
            Q(institucion__nombre__icontains=query) |
            Q(institucion__municipio__icontains=query)
        )

    if estado_filtro:
        fichas = fichas.filter(estado=estado_filtro)

    if instructor_filtro:
        fichas = fichas.filter(instructor_lider_id=instructor_filtro)

    # Rol y permisos para añadir
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    puede_crear = request.user.is_superuser or rol_nombre in ['Administrador', 'Coordinador']

    instructores = User.objects.filter(perfil__rol__nombre__icontains='Instructor')

    context = {
        'fichas': fichas,
        'query': query,
        'estado_filtro': estado_filtro,
        'instructor_filtro': instructor_filtro,
        'instructores': instructores,
        'total_fichas': Ficha.objects.count(),
        'fichas_ejecucion': Ficha.objects.filter(estado='En Ejecucion').count(),
        'fichas_terminadas': Ficha.objects.filter(estado='Terminada').count(),
        'puede_crear': puede_crear,
    }
    return render(request, 'academico/fichas_lista.html', context)


@login_required
def detalle_ficha(request, pk):
    """
    Expediente completo de una ficha técnica con 10 pestañas operativas:
    RESUMEN, APRENDICES, PROGRAMA, INSTRUCTORES, HORARIO, SEGUIMIENTO,
    EVALUACIONES, EVIDENCIAS, NOVEDADES, REPORTES.
    """
    ficha = get_object_or_404(
        Ficha.objects.select_related('programa', 'institucion', 'instructor_lider'),
        pk=pk
    )
    matriculas = ficha.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name')
    seguimientos = ficha.seguimientos.select_related('instructor', 'matricula__aprendiz').order_by('-fecha_visita')
    competencias = ficha.programa.competencias.prefetch_related('resultados').all()
    horarios = ficha.horarios.select_related('instructor').filter(activo=True).order_by('dia', 'hora_inicio')

    # Instructores relacionados (Líder + horarios)
    instructores = User.objects.filter(
        Q(id=ficha.instructor_lider_id) | Q(horarios_formativos__ficha=ficha)
    ).distinct()

    # Evaluaciones de la ficha
    evaluaciones = JuicioEvaluativo.objects.filter(
        matricula__ficha=ficha
    ).select_related('matricula__aprendiz', 'resultado_aprendizaje', 'instructor').order_by('-fecha_evaluacion')

    total_juicios = evaluaciones.count()
    juicios_aprobados = evaluaciones.filter(juicio_valor='A').count()
    juicios_deficientes = evaluaciones.filter(juicio_valor='D').count()
    porcentaje_aprobacion = round((juicios_aprobados / total_juicios * 100), 1) if total_juicios > 0 else 0

    # Novedades / Solicitudes vinculadas
    novedades = SolicitudSecretaria.objects.filter(ficha=ficha).select_related('aprendiz', 'responsable').order_by('-fecha_creacion')

    # Permisos
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    puede_editar = request.user.is_superuser or rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA']

    context = {
        'ficha': ficha,
        'matriculas': matriculas,
        'total_aprendices': matriculas.count(),
        'competencias': competencias,
        'instructores': instructores,
        'horarios': horarios,
        'seguimientos': seguimientos,
        'evaluaciones': evaluaciones[:30],
        'total_juicios': total_juicios,
        'juicios_aprobados': juicios_aprobados,
        'juicios_deficientes': juicios_deficientes,
        'porcentaje_aprobacion': porcentaje_aprobacion,
        'novedades': novedades,
        'puede_editar': puede_editar,
    }
    return render(request, 'academico/ficha_detalle.html', context)


@login_required
def editar_ficha(request, pk):
    """
    Edición de los metadatos de una ficha técnica: fechas, estado, instructor líder.
    """
    ficha = get_object_or_404(Ficha, pk=pk)
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    if not (request.user.is_superuser or rol_nombre in ['Administrador', 'Coordinador']):
        messages.error(request, "No tienes permisos para modificar los datos de la ficha técnica.")
        return redirect('fichas_detalle', pk=ficha.pk)

    if request.method == 'POST':
        form = FichaForm(request.POST, instance=ficha)
        if form.is_valid():
            form.save()
            RegistroAuditoria.objects.create(
                usuario=request.user,
                accion=f"Actualización de Ficha {ficha.codigo_ficha}",
                modulo="Fichas Técnicas",
                detalles=f"Estado: {ficha.estado}, Fechas: {ficha.fecha_inicio} a {ficha.fecha_fin}"
            )
            messages.success(request, f"La Ficha {ficha.codigo_ficha} ha sido actualizada exitosamente.")
            return redirect('fichas_detalle', pk=ficha.pk)
        else:
            messages.error(request, "Por favor revise los campos del formulario.")
    else:
        form = FichaForm(instance=ficha)

    return render(request, 'academico/ficha_formulario.html', {
        'form': form,
        'titulo': f'Editar Ficha Técnica {ficha.codigo_ficha}',
        'ficha': ficha,
    })


@login_required
def crear_ficha(request):
    """
    Apertura de una nueva ficha técnica de Media Técnica en el Centro.
    """
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    if not (request.user.is_superuser or rol_nombre in ['Administrador', 'Coordinador']):
        messages.error(request, "No tienes permisos para aperturar nuevas fichas técnicas.")
        return redirect('fichas_lista')

    if request.method == 'POST':
        form = FichaForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            RegistroAuditoria.objects.create(
                usuario=request.user,
                accion=f"Apertura de nueva Ficha {ficha.codigo_ficha}",
                modulo="Fichas Técnicas",
                detalles=f"Programa: {ficha.programa.denominacion}, Institución: {ficha.institucion.nombre}"
            )
            messages.success(request, f"Ficha {ficha.codigo_ficha} creada exitosamente.")
            return redirect('fichas_detalle', pk=ficha.pk)
        else:
            messages.error(request, "Por favor revise los campos obligatorios.")
    else:
        form = FichaForm()

    return render(request, 'academico/ficha_formulario.html', {'form': form, 'titulo': 'Apertura de Ficha Técnica'})


@login_required
def lista_programas(request):
    """
    Módulo de Programas de Formación Técnica del SENA (ADSI, Sistemas, etc.).
    """
    query = request.GET.get('q', '').strip()
    programas = ProgramaFormacion.objects.annotate(
        num_fichas=Count('fichas', distinct=True),
        num_competencias=Count('competencias', distinct=True)
    ).all().order_by('denominacion')

    if query:
        programas = programas.filter(
            Q(denominacion__icontains=query) |
            Q(codigo_programa__icontains=query)
        )

    context = {
        'programas': programas,
        'query': query,
        'total_programas': programas.count(),
    }
    return render(request, 'academico/programas_lista.html', context)


@login_required
def detalle_programa(request, pk):
    """
    Expediente Curricular de un Programa de Formación: competencias,
    resultados de aprendizaje, fichas asociadas y aprendices matriculados.
    """
    programa = get_object_or_404(
        ProgramaFormacion.objects.prefetch_related(
            'competencias__resultados',
            'fichas__institucion',
            'fichas__instructor_lider'
        ),
        pk=pk
    )
    fichas = programa.fichas.annotate(num_aprendices=Count('matriculas')).order_by('-fecha_inicio')
    total_aprendices = Matricula.objects.filter(ficha__programa=programa).count()
    competencias = programa.competencias.all()

    context = {
        'programa': programa,
        'fichas': fichas,
        'competencias': competencias,
        'total_aprendices': total_aprendices,
    }
    return render(request, 'academico/programa_detalle.html', context)


@login_required
def reporte_ficha_pdf(request, pk):
    """
    Exportación oficial en PDF del expediente y lista de aprendices de la ficha técnica.
    """
    ficha = get_object_or_404(Ficha.objects.select_related('programa', 'institucion', 'instructor_lider'), pk=pk)
    matriculas = ficha.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name')

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    ancho, alto = letter

    # Encabezado institucional SENA
    p.setFillColor(colors.HexColor('#39A900'))
    p.rect(0, alto - 50, ancho, 50, fill=True, stroke=False)
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, alto - 32, "SERVICIO NACIONAL DE APRENDIZAJE - SENA | SINETEC")
    p.setFont("Helvetica", 10)
    p.drawString(40, alto - 45, "Regional Magdalena · Centro de Logística y Promoción Ecoturística")

    # Datos de la Ficha
    p.setFillColor(colors.HexColor('#1E293B'))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, alto - 80, f"REPORTE OFICIAL DE FICHA TÉCNICA: {ficha.codigo_ficha}")
    p.setFont("Helvetica", 9)
    p.drawString(40, alto - 96, f"Programa: {ficha.programa.denominacion} (Cód SOFIA: {ficha.programa.codigo_programa})")
    p.drawString(40, alto - 110, f"Institución Articulada: {ficha.institucion.nombre} - {ficha.institucion.municipio}")
    p.drawString(40, alto - 124, f"Instructor Líder: {ficha.instructor_lider.get_full_name() or ficha.instructor_lider.username}")
    p.drawString(40, alto - 138, f"Vigencia: {ficha.fecha_inicio} a {ficha.fecha_fin} | Estado: {ficha.estado}")

    # Tabla de Aprendices
    y = alto - 170
    p.setFillColor(colors.HexColor('#F1F5F9'))
    p.rect(40, y - 5, ancho - 80, 18, fill=True, stroke=False)
    p.setFillColor(colors.HexColor('#0F172A'))
    p.setFont("Helvetica-Bold", 9)
    p.drawString(45, y, "No.")
    p.drawString(75, y, "Documento")
    p.drawString(170, y, "Apellidos y Nombres")
    p.drawString(380, y, "Correo Electrónico")
    p.drawString(500, y, "Estado")

    p.setFont("Helvetica", 8)
    for idx, mat in enumerate(matriculas, start=1):
        y -= 16
        if y < 50:
            p.showPage()
            y = alto - 60
        nombre = mat.aprendiz.get_full_name() or mat.aprendiz.username
        doc = f"{mat.aprendiz.perfil.tipo_documento} {mat.aprendiz.perfil.numero_documento}" if hasattr(mat.aprendiz, 'perfil') else "N/A"
        correo = mat.aprendiz.email or "Sin correo"

        p.setFillColor(colors.HexColor('#334155'))
        p.drawString(45, y, str(idx))
        p.drawString(75, y, doc)
        p.drawString(170, y, nombre[:36])
        p.drawString(380, y, correo[:28])
        p.drawString(500, y, mat.get_estado_formacion_display())

    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_ficha_{ficha.codigo_ficha}.pdf"'
    return response


@login_required
def reporte_ficha_excel(request, pk):
    """
    Exportación en Excel (.xlsx) del listado de aprendices y estado de la ficha.
    """
    ficha = get_object_or_404(Ficha.objects.select_related('programa', 'institucion', 'instructor_lider'), pk=pk)
    matriculas = ficha.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name')

    wb = Workbook()
    ws = wb.active
    ws.title = f"Ficha {ficha.codigo_ficha}"

    ws.append(["SERVICIO NACIONAL DE APRENDIZAJE - SENA | REGIONAL MAGDALENA"])
    ws.append([f"FICHA: {ficha.codigo_ficha} - {ficha.programa.denominacion}"])
    ws.append([f"Sede: {ficha.institucion.nombre} ({ficha.institucion.municipio}) | Instructor: {ficha.instructor_lider.get_full_name()}"])
    ws.append([])
    ws.append(["No.", "Tipo Doc", "Número Documento", "Apellidos y Nombres", "Correo Electrónico", "Teléfono", "Grado", "Estado"])

    for idx, mat in enumerate(matriculas, start=1):
        tdoc = mat.aprendiz.perfil.tipo_documento if hasattr(mat.aprendiz, 'perfil') else ""
        ndoc = mat.aprendiz.perfil.numero_documento if hasattr(mat.aprendiz, 'perfil') else ""
        tel = mat.aprendiz.perfil.telefono if hasattr(mat.aprendiz, 'perfil') else ""
        ws.append([
            idx,
            tdoc,
            ndoc,
            mat.aprendiz.get_full_name() or mat.aprendiz.username,
            mat.aprendiz.email,
            tel,
            mat.get_grado_escolar_display(),
            mat.get_estado_formacion_display()
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="aprendices_ficha_{ficha.codigo_ficha}.xlsx"'
    wb.save(response)
    return response


@login_required
def consulta_certificacion(request):
    """
    Consulta institucional del estado de cumplimiento de requisitos académicos
    para la certificación técnica de los aprendices en Media Técnica.
    """
    ficha_id = request.GET.get('ficha', '').strip()
    fichas = Ficha.objects.filter(estado='En Ejecucion').order_by('codigo_ficha')

    ficha_seleccionada = None
    aprendices_cert = []

    if ficha_id:
        ficha_seleccionada = Ficha.objects.filter(id=ficha_id).first()
    if not ficha_seleccionada:
        ficha_seleccionada = Ficha.objects.filter(codigo_ficha='3173430').first() or fichas.first()

    if ficha_seleccionada:
        raps_total = ResultadoAprendizaje.objects.filter(competencia__programa=ficha_seleccionada.programa).count()
        matriculas = ficha_seleccionada.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name')
        for m in matriculas:
            aprobados = JuicioEvaluativo.objects.filter(matricula=m, juicio_valor='A').count()
            pendientes = max(0, raps_total - aprobados)
            porcentaje = round((aprobados / raps_total * 100), 1) if raps_total > 0 else 0
            apto = (pendientes == 0 and raps_total > 0)
            aprendices_cert.append({
                'matricula': m,
                'raps_total': raps_total,
                'aprobados': aprobados,
                'pendientes': pendientes,
                'porcentaje': porcentaje,
                'apto': apto,
            })

    context = {
        'fichas': fichas,
        'ficha_seleccionada': ficha_seleccionada,
        'aprendices_cert': aprendices_cert,
    }
    return render(request, 'academico/certificacion.html', context)


@login_required
def tablero_horarios(request):
    horarios = HorarioFicha.objects.select_related('ficha', 'ficha__programa', 'instructor').filter(activo=True)
    ficha_id = request.GET.get('ficha', '').strip()
    if ficha_id:
        horarios = horarios.filter(ficha_id=ficha_id)
    fichas = Ficha.objects.filter(estado='En Ejecucion').order_by('codigo_ficha')
    return render(request, 'academico/horarios.html', {'horarios': horarios, 'fichas': fichas, 'ficha_id': ficha_id})


@login_required
def crear_horario(request):
    if request.method == 'POST':
        form = HorarioFichaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bloque agregado al horario de la ficha.')
            return redirect('horarios_tablero')
    else:
        form = HorarioFichaForm()
    return render(request, 'academico/horario_formulario.html', {'form': form})


@login_required
def eliminar_horario(request, pk):
    horario = get_object_or_404(HorarioFicha, pk=pk)
    if request.method == 'POST':
        horario.delete()
        messages.success(request, 'Bloque retirado del horario.')
    return redirect('horarios_tablero')


@login_required
def matricular_aprendiz(request, ficha_id):
    """
    Matrícula de un nuevo estudiante en una ficha técnica (RN-001, RN-002, RN-007).
    Crea el usuario, su perfil y la vinculación formal en una sola transacción segura.
    """
    ficha = get_object_or_404(Ficha, pk=ficha_id)
    import_form = ImportarAprendicesForm()
    import_errors = []

    if request.method == 'POST':
        if request.POST.get('accion') == 'importar':
            import_form = ImportarAprendicesForm(request.POST, request.FILES)
            if import_form.is_valid():
                try:
                    registros = leer_archivo_aprendices(import_form.cleaned_data['archivo'])
                    registros_validos, import_errors = validar_importacion_aprendices(registros)
                except (ValueError, csv.Error) as error:
                    import_errors = [str(error)]
                if not import_errors and registros_validos:
                    try:
                        with transaction.atomic():
                            rol_estudiante, _ = Rol.objects.get_or_create(
                                nombre='Estudiante',
                                defaults={'descripcion': 'Aprendiz matriculado en Media Técnica'},
                            )
                            for datos in registros_validos:
                                crear_matricula_desde_datos(ficha, datos, rol_estudiante)
                        messages.success(
                            request,
                            f'Se importaron {len(registros_validos)} aprendices en la Ficha {ficha.codigo_ficha}.',
                        )
                        return redirect('fichas_detalle', pk=ficha.pk)
                    except Exception as error:
                        import_errors = [f'No fue posible completar la importación: {error}']
                elif not import_errors:
                    import_errors = ['El archivo no contiene aprendices para importar.']
            return render(request, 'academico/matricular.html', {
                'form': MatriculaRapidaForm(),
                'import_form': import_form,
                'import_errors': import_errors,
                'ficha': ficha,
            })

        form = MatriculaRapidaForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    # Verificar si ya existe usuario con ese correo o documento
                    num_doc = cd['numero_documento'].strip()
                    if PerfilUsuario.objects.filter(numero_documento=num_doc).exists():
                        messages.error(request, f"Error (RN-001): Ya existe un usuario registrado con el documento {num_doc}.")
                        return render(request, 'academico/matricular.html', {
                            'form': form,
                            'import_form': import_form,
                            'import_errors': import_errors,
                            'ficha': ficha,
                        })

                    # Obtener o crear rol Estudiante
                    rol_estudiante, _ = Rol.objects.get_or_create(
                        nombre="Estudiante",
                        defaults={'descripcion': 'Aprendiz matriculado en Media Técnica'}
                    )

                    matricula = crear_matricula_desde_datos(ficha, cd, rol_estudiante)
                    nombre_aprendiz = matricula.aprendiz.get_full_name() or matricula.aprendiz.username
                    messages.success(request, f"Aprendiz {nombre_aprendiz} matriculado exitosamente en la Ficha {ficha.codigo_ficha}.")
                    return redirect('fichas_detalle', pk=ficha.pk)

            except Exception as e:
                messages.error(request, f"Ocurrió un error al procesar la matrícula: {str(e)}")
    else:
        form = MatriculaRapidaForm()

    return render(request, 'academico/matricular.html', {
        'form': form,
        'import_form': import_form,
        'import_errors': import_errors,
        'ficha': ficha,
    })
