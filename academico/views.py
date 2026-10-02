import csv
import io
import unicodedata
import uuid
from datetime import date, datetime
from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import os
from django.conf import settings
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse

from .models import (
    Ficha, Matricula, ProgramaFormacion, Competencia, ResultadoAprendizaje,
    HorarioFicha, CargaAcademica, GRADOS_POR_NIVEL, SECCIONES_ESCOLARES,
)
from openpyxl import load_workbook, Workbook
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
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
    Listado general de Fichas de Media Técnica con 4 KPIs en tiempo real,
    filtros avanzados (institución, programa, estado), ordenamiento y paginación.
    """
    query = request.GET.get('q', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    instructor_filtro = request.GET.get('instructor', '').strip()
    institucion_filtro = request.GET.get('institucion', '').strip()
    programa_filtro = request.GET.get('programa', '').strip()
    orden = request.GET.get('orden', 'recientes').strip()

    from instituciones.models import InstitucionEducativa

    # KPIs Globales
    total_fichas = Ficha.objects.count()
    fichas_ejecucion = Ficha.objects.filter(estado='En Ejecucion').count()
    fichas_terminadas = Ficha.objects.filter(estado='Terminada').count()
    fichas_canceladas = Ficha.objects.filter(estado='Cancelada').count()

    fichas = Ficha.objects.select_related(
        'programa', 'institucion', 'instructor_lider'
    ).annotate(
        num_aprendices=Count('matriculas', distinct=True),
        num_horarios=Count('horarios', distinct=True)
    ).all()

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

    if institucion_filtro:
        fichas = fichas.filter(institucion_id=institucion_filtro)

    if programa_filtro:
        fichas = fichas.filter(programa_id=programa_filtro)

    # Ordenamiento
    if orden == 'codigo_asc':
        fichas = fichas.order_by('codigo_ficha')
    elif orden == 'codigo_desc':
        fichas = fichas.order_by('-codigo_ficha')
    elif orden == 'aprendices_desc':
        fichas = fichas.order_by('-num_aprendices', '-fecha_inicio')
    else:  # recientes
        fichas = fichas.order_by('-fecha_inicio', '-id')

    # Paginación (10 por página)
    paginator = Paginator(fichas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Rol y permisos para añadir
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    puede_crear = request.user.is_superuser or rol_nombre in ['Administrador', 'Coordinador']

    instructores = User.objects.filter(perfil__rol__nombre__icontains='Instructor')
    instituciones = InstitucionEducativa.objects.filter(activa=True).order_by('nombre')
    programas = ProgramaFormacion.objects.all().order_by('denominacion')

    context = {
        'page_obj': page_obj,
        'fichas': page_obj,
        'query': query,
        'estado_filtro': estado_filtro,
        'instructor_filtro': instructor_filtro,
        'institucion_filtro': institucion_filtro,
        'programa_filtro': programa_filtro,
        'orden': orden,
        'instructores': instructores,
        'instituciones': instituciones,
        'programas': programas,
        'total_fichas': total_fichas,
        'fichas_ejecucion': fichas_ejecucion,
        'fichas_terminadas': fichas_terminadas,
        'fichas_canceladas': fichas_canceladas,
        'puede_crear': puede_crear,
    }
    return render(request, 'academico/fichas_lista.html', context)


@login_required
def detalle_ficha(request, pk):
    """
    Expediente completo de una ficha técnica con pestañas operativas y modal rápido de matrícula.
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

    # Historial y auditoría de la ficha
    from seguimiento.models import RegistroAuditoria
    historial = RegistroAuditoria.objects.filter(
        Q(detalles__icontains=ficha.codigo_ficha) |
        Q(modulo__icontains='Ficha')
    ).select_related('usuario').order_by('-fecha')[:15]

    # Aprendices disponibles para matricular (que no estén ya en esta ficha)
    aprendices_disponibles = User.objects.filter(
        perfil__rol__nombre__icontains='Estudiante'
    ).exclude(
        matriculas_academicas__ficha=ficha
    ).select_related('perfil').order_by('last_name', 'first_name')[:80]

    context = {
        'ficha': ficha,
        'matriculas': matriculas,
        'total_aprendices': matriculas.count(),
        'competencias': competencias,
        'instructores': instructores,
        'horarios': horarios,
        'seguimientos': seguimientos,
        'total_seguimientos': seguimientos.count(),
        'historial': historial,
        'evaluaciones': evaluaciones[:30],
        'total_juicios': total_juicios,
        'juicios_aprobados': juicios_aprobados,
        'juicios_deficientes': juicios_deficientes,
        'porcentaje_aprobacion': porcentaje_aprobacion,
        'novedades': novedades,
        'puede_editar': puede_editar,
        'aprendices_disponibles': aprendices_disponibles,
    }
    return render(request, 'academico/ficha_detalle.html', context)


@login_required
def cambiar_estado_ficha(request, pk):
    """
    Alterna o actualiza el estado de una ficha técnica (En Ejecucion, Terminada, Cancelada) con auditoría.
    """
    ficha = get_object_or_404(Ficha, pk=pk)
    nuevo_estado = request.GET.get('estado') or request.POST.get('estado')
    if nuevo_estado in ['En Ejecucion', 'Terminada', 'Cancelada']:
        ficha.estado = nuevo_estado
    else:
        if ficha.estado == 'En Ejecucion':
            ficha.estado = 'Terminada'
        elif ficha.estado == 'Terminada':
            ficha.estado = 'En Ejecucion'
        else:
            ficha.estado = 'En Ejecucion'
    ficha.save()

    from seguimiento.models import RegistroAuditoria
    RegistroAuditoria.registrar(
        usuario=request.user,
        modulo='Fichas Técnicas',
        accion=f'Cambio de Estado a {ficha.estado}',
        detalles=f"Se modificó el estado de la ficha técnica {ficha.codigo_ficha} a '{ficha.estado}'.",
        request=request
    )
    messages.success(request, f"La Ficha {ficha.codigo_ficha} ahora está en estado '{ficha.estado}'.")

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('fichas_detalle', pk=ficha.pk)


@login_required
def eliminar_ficha(request, pk):
    """
    Eliminación segura de una ficha técnica con protección referencial.
    Si contiene aprendices o seguimientos vinculados, rechaza el borrado.
    """
    ficha = get_object_or_404(Ficha, pk=pk)
    matriculas_count = ficha.matriculas.count()
    seguimientos_count = ficha.seguimientos.count()

    if matriculas_count > 0 or seguimientos_count > 0:
        messages.warning(
            request,
            f"No es posible eliminar la Ficha {ficha.codigo_ficha} porque contiene {matriculas_count} aprendiz(ces) "
            f"o {seguimientos_count} seguimiento(s) asociado(s). Para archivarla sin perder datos, cambie su estado a 'Cancelada'."
        )
        return redirect('fichas_detalle', pk=ficha.pk)

    if request.method == 'POST':
        codigo = ficha.codigo_ficha
        ficha.delete()
        from seguimiento.models import RegistroAuditoria
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Fichas Técnicas',
            accion='Eliminación de Ficha',
            detalles=f"Se eliminó la ficha técnica {codigo} del sistema.",
            request=request
        )
        messages.success(request, f"La Ficha {codigo} ha sido eliminada exitosamente del sistema.")
        return redirect('fichas_lista')

    return render(request, 'academico/confirmar_eliminar_ficha.html', {'ficha': ficha})


@login_required
def agregar_aprendiz_rapido(request, pk):
    """
    Permite matricular un aprendiz existente o crear uno nuevo en un solo paso
    directamente desde el expediente de la ficha técnica.
    """
    ficha = get_object_or_404(Ficha, pk=pk)
    if request.method == 'POST':
        modo = request.POST.get('modo', 'existente')
        from seguimiento.models import RegistroAuditoria
        if modo == 'existente':
            aprendiz_id = request.POST.get('aprendiz_id')
            if not aprendiz_id:
                messages.error(request, "Debe seleccionar un aprendiz de la lista.")
                return redirect('fichas_detalle', pk=ficha.pk)

            if Matricula.objects.filter(ficha=ficha, aprendiz_id=aprendiz_id).exists():
                messages.warning(request, "El aprendiz ya se encuentra matriculado en esta ficha.")
                return redirect('fichas_detalle', pk=ficha.pk)

            aprendiz_user = get_object_or_404(User, pk=aprendiz_id)
            Matricula.objects.create(
                ficha=ficha,
                aprendiz=aprendiz_user,
                grado_escolar=request.POST.get('grado_escolar', '10')
            )
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Fichas Técnicas',
                accion='Matrícula de Aprendiz',
                detalles=f"Se vinculó a {aprendiz_user.get_full_name() or aprendiz_user.username} a la Ficha {ficha.codigo_ficha}.",
                request=request
            )
            messages.success(request, f"Aprendiz {aprendiz_user.get_full_name() or aprendiz_user.username} matriculado exitosamente.")
        elif modo == 'nuevo':
            num_doc = request.POST.get('numero_documento', '').strip()
            nombres = request.POST.get('nombres', '').strip()
            apellidos = request.POST.get('apellidos', '').strip()
            correo = request.POST.get('correo', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            tipo_doc = request.POST.get('tipo_documento', 'TI').strip()
            grado = request.POST.get('grado_escolar', '10').strip()

            if not (num_doc and nombres and apellidos):
                messages.error(request, "Documento, nombres y apellidos son campos obligatorios.")
                return redirect('fichas_detalle', pk=ficha.pk)

            if PerfilUsuario.objects.filter(numero_documento=num_doc).exists():
                messages.warning(request, f"Ya existe un aprendiz con el documento {num_doc}. Búsquelo en la opción de vincular existente.")
                return redirect('fichas_detalle', pk=ficha.pk)

            with transaction.atomic():
                username = f"ap_{num_doc}"
                if User.objects.filter(username=username).exists():
                    username = f"ap_{num_doc}_{ficha.id}"
                user = User.objects.create_user(
                    username=username,
                    email=correo,
                    first_name=nombres,
                    last_name=apellidos,
                    password=f"Sena{num_doc[:4]}*"
                )
                rol_estudiante, _ = Rol.objects.get_or_create(
                    nombre='Estudiante',
                    defaults={'descripcion': 'Aprendiz matriculado en Media Técnica'}
                )
                perfil = user.perfil
                perfil.rol = rol_estudiante
                perfil.tipo_documento = tipo_doc
                perfil.numero_documento = num_doc
                perfil.telefono = telefono
                perfil.save()

                Matricula.objects.create(
                    ficha=ficha,
                    aprendiz=user,
                    grado_escolar=grado
                )
                RegistroAuditoria.registrar(
                    usuario=request.user,
                    modulo='Fichas Técnicas',
                    accion='Registro y Matrícula Rápida',
                    detalles=f"Se creó y matriculó al aprendiz {nombres} {apellidos} ({num_doc}) en la Ficha {ficha.codigo_ficha}.",
                    request=request
                )
                messages.success(request, f"Aprendiz {nombres} {apellidos} registrado y matriculado en la Ficha {ficha.codigo_ficha}.")
    return redirect('fichas_detalle', pk=ficha.pk)


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


def _parse_hora(valor):
    valor = (valor or '').strip().upper().replace('.', '')
    for fmt in ('%H:%M', '%H:%M:%S', '%I:%M %p', '%I:%M%p'):
        try:
            return datetime.strptime(valor, fmt).time()
        except ValueError:
            continue
    return None


def _docentes_activos():
    return User.objects.filter(
        Q(perfil__rol__nombre__icontains='Instructor') |
        Q(perfil__rol__nombre__icontains='Profesor') |
        Q(perfil__rol__nombre__icontains='Docente')
    ).distinct().order_by('last_name', 'first_name')


@login_required
def lista_cursos(request):
    """Malla curricular visual: materias activas y sus grupos asociados."""
    if request.method == 'POST':
        denominacion = (request.POST.get('denominacion') or '').strip()
        tipo_programa = request.POST.get('tipo_programa') or 'Técnico'
        if not denominacion:
            messages.error(request, 'El nombre del curso es obligatorio.')
        else:
            ProgramaFormacion.objects.create(
                codigo_programa=f'CUR-{uuid.uuid4().hex[:8].upper()}',
                denominacion=denominacion,
                tipo_programa=tipo_programa,
                activo=True,
            )
            messages.success(request, f'El curso "{denominacion}" fue creado correctamente.')
        return redirect('cursos_lista')

    query = (request.GET.get('q') or '').strip()
    cursos = ProgramaFormacion.objects.filter(activo=True).prefetch_related('fichas').annotate(
        total_fichas=Count('fichas', distinct=True),
        total_competencias=Count('competencias', distinct=True),
    ).order_by('denominacion')
    if query:
        cursos = cursos.filter(denominacion__icontains=query)

    return render(request, 'academico/cursos_lista.html', {
        'cursos': cursos,
        'query': query,
        'total_cursos': ProgramaFormacion.objects.filter(activo=True).count(),
        'grupos_primaria': CargaAcademica.objects.filter(nivel='Primaria').count(),
        'grupos_secundaria': CargaAcademica.objects.filter(nivel='Secundaria').count(),
    })


@login_required
def lista_programas(request):
    """Carga académica: asignación de docentes a materias, grados y secciones."""
    if request.method == 'POST':
        profesor_id = request.POST.get('profesor_id')
        programa_id = request.POST.get('programa_id') or request.POST.get('curso_id')
        nivel = (request.POST.get('nivel') or '').strip()
        grado = (request.POST.get('grado') or '').strip()
        seccion = (request.POST.get('seccion') or 'A').strip() or 'A'

        if not all([profesor_id, programa_id, nivel, grado, seccion]):
            messages.error(request, 'Todos los campos son obligatorios para asignar la carga académica.')
        elif CargaAcademica.objects.filter(
            programa_id=programa_id,
            grado=grado,
            seccion=seccion,
            anio_lectivo=2026
        ).exists():
            carga_exist = CargaAcademica.objects.filter(
                programa_id=programa_id, grado=grado, seccion=seccion, anio_lectivo=2026
            ).select_related('profesor', 'programa').first()
            nom_p = carga_exist.profesor.get_full_name() if carga_exist.profesor else 'Otro docente'
            messages.error(request, f'No se puede duplicar la asignación: La materia "{carga_exist.programa.denominacion}" ya está asignada al {grado} Sección "{seccion}" a cargo de {nom_p}.')
        else:
            # Validar límite de materias por profesor (máximo 2 materias distintas)
            materias_actuales = set(
                CargaAcademica.objects.filter(profesor_id=profesor_id)
                .exclude(programa_id__isnull=True)
                .values_list('programa_id', flat=True)
            )
            try:
                prog_int = int(programa_id)
            except (ValueError, TypeError):
                prog_int = None
            if prog_int and prog_int not in materias_actuales and len(materias_actuales) >= 2:
                messages.error(request, 'El docente ya está inscrito en el número máximo de materias permitidas (máximo 2 materias distintas). Ya está inscrito en otras asignaturas.')
                return redirect('programas_lista')

            CargaAcademica.objects.create(
                profesor_id=profesor_id,
                programa_id=programa_id,
                nivel=nivel,
                grado=grado,
                seccion=seccion,
                anio_lectivo=2026,
            )
            messages.success(request, 'Carga académica asignada.')
        return redirect('programas_lista')

    docentes = _docentes_activos()
    if not docentes.exists():
        docentes = User.objects.exclude(
            perfil__rol__nombre='Estudiante'
        ).order_by('last_name', 'first_name')
    cargas = CargaAcademica.objects.select_related('profesor', 'profesor__perfil', 'programa')
    context = {
        'docentes': docentes,
        'programas': ProgramaFormacion.objects.filter(activo=True).order_by('denominacion'),
        'grados_por_nivel': GRADOS_POR_NIVEL,
        'secciones': SECCIONES_ESCOLARES,
        'cargas_primaria': cargas.filter(nivel='Primaria'),
        'cargas_secundaria': cargas.filter(nivel='Secundaria'),
        'cargas_inicial': cargas.filter(nivel='Inicial'),
    }
    return render(request, 'academico/malla_curricular.html', context)


@login_required
def eliminar_carga_academica(request, pk):
    carga = get_object_or_404(CargaAcademica, pk=pk)
    if request.method == 'POST':
        carga.delete()
        messages.success(request, 'Asignación académica retirada.')
    return redirect('programas_lista')


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

    # Encabezado institucional SINETEC
    p.setFillColor(colors.HexColor('#1E3A8A'))
    p.rect(0, alto - 60, ancho, 60, fill=True, stroke=False)

    # Logo SENA Oficial en el encabezado
    logo_sena_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'sena_logo_white.png')
    if os.path.exists(logo_sena_path):
        try:
            sena_img = ImageReader(logo_sena_path)
            p.drawImage(sena_img, ancho - 65, alto - 52, width=44, height=44, mask='auto')
        except Exception:
            pass

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, alto - 28, "SERVICIO NACIONAL DE APRENDIZAJE - SENA | SINETEC")
    p.setFont("Helvetica", 10)
    p.drawString(40, alto - 45, "Regional Magdalena · Centro de Logística y Promoción Ecoturística")

    # Datos de la Ficha
    p.setFillColor(colors.HexColor('#1E293B'))
    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, alto - 85, f"REPORTE OFICIAL DE FICHA TÉCNICA: {ficha.codigo_ficha}")
    p.setFont("Helvetica", 9)
    p.drawString(40, alto - 100, f"Programa: {ficha.programa.denominacion} (Cód SOFIA: {ficha.programa.codigo_programa})")
    p.drawString(40, alto - 114, f"Institución Articulada: {ficha.institucion.nombre} - {ficha.institucion.municipio}")
    p.drawString(40, alto - 128, f"Instructor Líder: {ficha.instructor_lider.get_full_name() or ficha.instructor_lider.username}")
    p.drawString(40, alto - 142, f"Vigencia: {ficha.fecha_inicio} a {ficha.fecha_fin} | Estado: {ficha.estado}")

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


def _redirigir_horarios(request, extra=None):
    params = extra or {}
    for key in ('nivel', 'grado', 'seccion', 'dia'):
        valor = request.POST.get(key) or request.GET.get(key) or params.get(key)
        if valor:
            params[key] = valor
    qs = urlencode({k: v for k, v in params.items() if v})
    return redirect(f'/academico/horarios/?{qs}' if qs else 'horarios_tablero')


@login_required
def tablero_horarios(request):
    nivel = (request.GET.get('nivel') or '').strip()
    grado = (request.GET.get('grado') or '').strip()
    seccion = (request.GET.get('seccion') or 'A').strip() or 'A'
    dia = (request.GET.get('dia') or '').strip()
    docente_id = request.GET.get('docente')
    aula_filtro = request.GET.get('aula')
    materia_id = request.GET.get('materia')
    q = request.GET.get('q', '').strip()

    # Detección de rol institucional para aislamiento estricto
    rol_obj = getattr(getattr(request.user, 'perfil', None), 'rol', None)
    rol_nombre = rol_obj.nombre if rol_obj else ''
    es_docente = not request.user.is_superuser and ('Docente' in rol_nombre or 'Instructor' in rol_nombre or 'Profesor' in rol_nombre)

    if es_docente:
        # Aislamiento estricto: el docente SOLO ve sus propias clases (y solo 10/11 como requiere la regla)
        docente_id = str(request.user.id)
        horarios_qs = HorarioFicha.objects.select_related(
            'ficha', 'ficha__programa', 'instructor', 'instructor__perfil', 'programa'
        ).filter(
            instructor=request.user, 
            activo=True,
            grado__in=['10', '11', '10mo Grado', '11mo Grado', '10°', '11°', 'Décimo', 'Undécimo']
        )
    else:
        # Administrador / Coordinador
        horarios_qs = HorarioFicha.objects.select_related(
            'ficha', 'ficha__programa', 'instructor', 'instructor__perfil', 'programa'
        ).filter(activo=True)

    # Si no hay filtros, preseleccionar un grado/curso para que siempre tenga contenido visible
    if not nivel and not grado and not docente_id and not aula_filtro and not q:
        primer_h = horarios_qs.first()
        if primer_h and primer_h.nivel and primer_h.grado:
            nivel = primer_h.nivel
            grado = primer_h.grado
            seccion = primer_h.seccion or 'A'
        else:
            nivel = 'Secundaria'
            grado = '10mo Grado'
            seccion = 'A'

    if nivel:
        horarios_qs = horarios_qs.filter(nivel=nivel)
    if grado:
        horarios_qs = horarios_qs.filter(grado=grado)
    if seccion:
        horarios_qs = horarios_qs.filter(seccion=seccion)
    if dia and dia != 'todos':
        horarios_qs = horarios_qs.filter(dia=dia)
    if docente_id and not es_docente:
        horarios_qs = horarios_qs.filter(instructor_id=docente_id)
    if aula_filtro:
        horarios_qs = horarios_qs.filter(ambiente__icontains=aula_filtro)
    if materia_id:
        horarios_qs = horarios_qs.filter(programa_id=materia_id)
    if q:
        horarios_qs = horarios_qs.filter(
            Q(tema__icontains=q) |
            Q(programa__denominacion__icontains=q) |
            Q(ambiente__icontains=q) |
            Q(instructor__first_name__icontains=q) |
            Q(instructor__last_name__icontains=q)
        )

    # Rejilla semanal completa (Lunes a Viernes)
    horarios_por_dia = {
        '1': horarios_qs.filter(dia='1').order_by('hora_inicio'),
        '2': horarios_qs.filter(dia='2').order_by('hora_inicio'),
        '3': horarios_qs.filter(dia='3').order_by('hora_inicio'),
        '4': horarios_qs.filter(dia='4').order_by('hora_inicio'),
        '5': horarios_qs.filter(dia='5').order_by('hora_inicio'),
    }

    if es_docente:
        docentes = User.objects.filter(id=request.user.id)
        programas_ids = HorarioFicha.objects.filter(instructor=request.user, activo=True).values_list('programa_id', flat=True)
        programas = ProgramaFormacion.objects.filter(id__in=programas_ids).order_by('denominacion')
        if not programas.exists():
            from academico.models import CargaAcademica
            prog_cargas = CargaAcademica.objects.filter(profesor=request.user).values_list('programa_id', flat=True)
            programas = ProgramaFormacion.objects.filter(id__in=prog_cargas).order_by('denominacion')
    else:
        docentes = _docentes_activos()
        if not docentes.exists():
            docentes = User.objects.exclude(perfil__rol__nombre='Estudiante').order_by('last_name', 'first_name')
        programas = ProgramaFormacion.objects.filter(activo=True).order_by('denominacion')
        if not programas.exists():
            programas = ProgramaFormacion.objects.all().order_by('denominacion')

    aulas_disponibles = [
        'Aula 101', 'Aula 102', 'Aula 103', 'Aula 104',
        'Aula 201', 'Aula 202', 'Aula 203', 'Aula 204',
        'Laboratorio de Ciencias', 'Sala de Informática 1', 'Sala de Informática 2',
        'Cancha Múltiple / Polideportivo', 'Biblioteca Central', 'Auditorio'
    ]

    horas_inicio_sugeridas = [
        '06:00', '06:30', '07:00', '07:30', '08:00', '08:30',
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '12:00', '12:30', '13:00', '13:30', '14:00', '14:30',
        '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00'
    ]

    return render(request, 'academico/horarios.html', {
        'horarios': horarios_qs.order_by('dia', 'hora_inicio'),
        'horarios_por_dia': horarios_por_dia,
        'docentes': docentes,
        'programas': programas,
        'aulas': aulas_disponibles,
        'horas_sugeridas': horas_inicio_sugeridas,
        'nivel': nivel,
        'grado': grado,
        'seccion': seccion,
        'dia': dia,
        'docente_sel': docente_id,
        'aula_sel': aula_filtro,
        'q': q,
        'grados_por_nivel': GRADOS_POR_NIVEL,
        'secciones': SECCIONES_ESCOLARES,
        'dias': HorarioFicha.DIAS,
    })


@login_required
def crear_horario(request):
    if request.method != 'POST':
        return redirect('horarios_tablero')

    nivel = (request.POST.get('nivel') or '').strip()
    grado = (request.POST.get('grado') or '').strip()
    seccion = (request.POST.get('seccion') or 'A').strip() or 'A'
    dia = (request.POST.get('dia') or '1').strip() or '1'
    hora_inicio = _parse_hora(request.POST.get('hora_inicio'))
    hora_fin = _parse_hora(request.POST.get('hora_fin'))
    es_recreo = request.POST.get('es_recreo') in ('1', 'on', 'true', 'True')
    programa_id = request.POST.get('programa_id')
    docente_id = request.POST.get('docente_id')
    aula = (request.POST.get('aula') or request.POST.get('ambiente') or 'Aula 101').strip()
    materia_texto = (request.POST.get('materia') or request.POST.get('tema') or '').strip()

    if not nivel or not grado:
        messages.error(request, 'Selecciona el nivel y grado antes de guardar el bloque horario.')
        return _redirigir_horarios(request)
    if not hora_inicio or not hora_fin:
        messages.error(request, 'Indica hora de inicio y hora de fin válidas (a partir de las 06:00 AM).')
        return _redirigir_horarios(request)
    if hora_fin <= hora_inicio:
        messages.error(request, 'La hora de finalización debe ser posterior a la hora de inicio.')
        return _redirigir_horarios(request)

    programa = None
    if programa_id:
        programa = ProgramaFormacion.objects.filter(pk=programa_id).first()
        if programa and not materia_texto:
            materia_texto = programa.denominacion

    if es_recreo:
        materia_texto = 'RECREO / DESCANSO PEDAGÓGICO'

    # Identificar docente asignado o seleccionado
    instructor = None
    if docente_id:
        instructor = User.objects.filter(pk=docente_id).first()
    if not instructor and programa:
        carga = CargaAcademica.objects.filter(
            nivel=nivel, grado=grado, seccion=seccion, programa=programa
        ).select_related('profesor').first()
        if carga:
            instructor = carga.profesor

    # ==========================================
    # CONTROL DE CONFLICTOS ADMINISTRATIVOS
    # ==========================================
    dia_nombre = dict(HorarioFicha.DIAS).get(dia, 'el día seleccionado')

    # 0. Límite de materias del docente (máximo 2 materias distintas)
    if instructor and programa and not es_recreo:
        materias_doc = set(
            CargaAcademica.objects.filter(profesor=instructor)
            .exclude(programa_id__isnull=True)
            .values_list('programa_id', flat=True)
        ) | set(
            HorarioFicha.objects.filter(instructor=instructor, activo=True)
            .exclude(programa_id__isnull=True)
            .values_list('programa_id', flat=True)
        )
        if programa.id not in materias_doc and len(materias_doc) >= 2:
            messages.error(request, f'El docente {instructor.get_full_name() or instructor.username} ya está inscrito en el número máximo de materias permitidas (máximo 2 materias distintas). Ya está inscrito en otras asignaturas.')
            return _redirigir_horarios(request)

    # 1. Conflicto de Docente (el docente no puede tener dos clases al mismo tiempo)
    if instructor and not es_recreo:
        conflicto_doc = HorarioFicha.objects.filter(
            instructor=instructor,
            dia=dia,
            activo=True,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        ).first()
        if conflicto_doc:
            messages.error(
                request,
                f"⚠️ CONFLICTO DE HORARIO: El docente {instructor.get_full_name()} ya tiene asignada la clase de '{conflicto_doc.nombre_materia}' en {conflicto_doc.grado} Sección '{conflicto_doc.seccion}' de {conflicto_doc.hora_inicio:%H:%M} a {conflicto_doc.hora_fin:%H:%M} el {dia_nombre}."
            )
            return _redirigir_horarios(request)

    # 2. Conflicto de Aula (el aula no puede ser ocupada por dos grupos al mismo tiempo)
    if aula and not es_recreo:
        conflicto_aula = HorarioFicha.objects.filter(
            ambiente__iexact=aula,
            dia=dia,
            activo=True,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        ).first()
        if conflicto_aula:
            messages.error(
                request,
                f"⚠️ CONFLICTO DE AULA: El espacio '{aula}' ya se encuentra ocupado por el grupo {conflicto_aula.grado} '{conflicto_aula.seccion}' ({conflicto_aula.nombre_materia}) en ese mismo bloque horario el {dia_nombre}."
            )
            return _redirigir_horarios(request)

    # 3. Conflicto de Grupo (el mismo grupo no puede tener dos clases a la misma hora)
    conflicto_grupo = HorarioFicha.objects.filter(
        grado=grado,
        seccion=seccion,
        dia=dia,
        activo=True,
        hora_inicio__lt=hora_fin,
        hora_fin__gt=hora_inicio
    ).first()
    if conflicto_grupo:
        messages.error(
            request,
            f"⚠️ CONFLICTO DE GRUPO: El grupo {grado} Sección '{seccion}' ya tiene programada la clase de '{conflicto_grupo.nombre_materia}' de {conflicto_grupo.hora_inicio:%H:%M} a {conflicto_grupo.hora_fin:%H:%M} el {dia_nombre}."
        )
        return _redirigir_horarios(request)

    # Vincular cohorte / curso institucional
    grado_num = ''.join(c for c in grado if c.isdigit())
    ficha = Ficha.objects.filter(
        Q(codigo_ficha__icontains=f"{grado_num}-{seccion}") |
        Q(codigo_ficha__icontains=f"{grado_num}{seccion}") |
        Q(codigo_ficha=f"{grado_num}-{seccion}")
    ).first()
    if not ficha:
        ficha = Ficha.objects.filter(estado='En Ejecucion').first()

    nueva_clase = HorarioFicha.objects.create(
        ficha=ficha,
        instructor=instructor,
        programa=programa,
        dia=dia,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        ambiente=aula,
        modalidad='Presencial',
        tema=materia_texto,
        nivel=nivel,
        grado=grado,
        seccion=seccion,
        es_recreo=es_recreo,
        activo=True,
        color_hex=request.POST.get('color_hex', '#E2E8F0'),
    )

    # Notificación al docente y registro de auditoría
    try:
        from seguimiento.models import Notificacion, RegistroAuditoria
        if instructor:
            Notificacion.objects.create(
                usuario=instructor,
                titulo=f"Nueva Clase en Horario: {materia_texto}",
                mensaje=f"Se agregó a su horario escolar la clase de {materia_texto} para {grado} '{seccion}' ({dia_nombre} {hora_inicio:%H:%M} - {hora_fin:%H:%M} en {aula}).",
                enlace="/instructor/",
                tipo="info"
            )
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo="Horarios",
            accion="Creación de Clase en Horario",
            detalles=f"Programó {materia_texto} en {grado} '{seccion}' ({dia_nombre} {hora_inicio:%H:%M} - {hora_fin:%H:%M}, {aula}).",
            request=request
        )
    except Exception:
        pass

    messages.success(request, f"¡Clase de '{materia_texto}' agregada al horario de {grado} '{seccion}' ({dia_nombre} {hora_inicio:%H:%M} - {hora_fin:%H:%M})!")
    return _redirigir_horarios(request)


@login_required
def editar_horario(request, pk):
    """Permite editar docente, aula, día, hora o asignatura de un bloque horario."""
    horario = get_object_or_404(HorarioFicha, pk=pk)

    if request.method == 'POST':
        nivel = (request.POST.get('nivel') or horario.nivel).strip()
        grado = (request.POST.get('grado') or horario.grado).strip()
        seccion = (request.POST.get('seccion') or horario.seccion).strip()
        dia = (request.POST.get('dia') or horario.dia).strip()
        hora_inicio = _parse_hora(request.POST.get('hora_inicio')) or horario.hora_inicio
        hora_fin = _parse_hora(request.POST.get('hora_fin')) or horario.hora_fin
        es_recreo = request.POST.get('es_recreo') in ('1', 'on', 'true', 'True')
        programa_id = request.POST.get('programa_id')
        docente_id = request.POST.get('docente_id')
        aula = (request.POST.get('aula') or request.POST.get('ambiente') or horario.ambiente).strip()
        materia_texto = (request.POST.get('materia') or request.POST.get('tema') or '').strip()

        if hora_fin <= hora_inicio:
            messages.error(request, 'La hora de fin debe ser posterior a la de inicio.')
            return redirect('horario_editar', pk=pk)

        programa = horario.programa
        if programa_id:
            programa = ProgramaFormacion.objects.filter(pk=programa_id).first()
            if programa and not materia_texto:
                materia_texto = programa.denominacion

        instructor = horario.instructor
        if docente_id:
            instructor = User.objects.filter(pk=docente_id).first()

        dia_nombre = dict(HorarioFicha.DIAS).get(dia, 'el día seleccionado')

        # Límite de materias del docente (máximo 2 materias distintas)
        if instructor and programa and not es_recreo:
            materias_doc = set(
                CargaAcademica.objects.filter(profesor=instructor)
                .exclude(programa_id__isnull=True)
                .values_list('programa_id', flat=True)
            ) | set(
                HorarioFicha.objects.filter(instructor=instructor, activo=True)
                .exclude(pk=pk)
                .exclude(programa_id__isnull=True)
                .values_list('programa_id', flat=True)
            )
            if programa.id not in materias_doc and len(materias_doc) >= 2:
                messages.error(request, f'El docente {instructor.get_full_name() or instructor.username} ya está inscrito en el número máximo de materias permitidas (máximo 2 materias distintas). Ya está inscrito en otras asignaturas.')
                return redirect('horario_editar', pk=pk)

        # Conflictos excluyendo el horario actual
        if instructor and not es_recreo:
            c_doc = HorarioFicha.objects.filter(
                instructor=instructor, dia=dia, activo=True,
                hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
            ).exclude(pk=pk).first()
            if c_doc:
                messages.error(request, f"Conflicto de Docente: {instructor.get_full_name()} ya tiene clase en ese horario ({c_doc.nombre_materia} en {c_doc.grado}).")
                return redirect('horario_editar', pk=pk)

        if aula and not es_recreo:
            c_aul = HorarioFicha.objects.filter(
                ambiente__iexact=aula, dia=dia, activo=True,
                hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
            ).exclude(pk=pk).first()
            if c_aul:
                messages.error(request, f"Conflicto de Aula: El espacio '{aula}' ya está reservado por {c_aul.grado} '{c_aul.seccion}'.")
                return redirect('horario_editar', pk=pk)

        c_grp = HorarioFicha.objects.filter(
            grado=grado, seccion=seccion, dia=dia, activo=True,
            hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio
        ).exclude(pk=pk).first()
        if c_grp:
            messages.error(request, f"Conflicto de Grupo: {grado} '{seccion}' ya tiene la materia '{c_grp.nombre_materia}' a esa misma hora.")
            return redirect('horario_editar', pk=pk)

        horario.nivel = nivel
        horario.grado = grado
        horario.seccion = seccion
        horario.dia = dia
        horario.hora_inicio = hora_inicio
        horario.hora_fin = hora_fin
        horario.ambiente = aula
        horario.programa = programa
        horario.instructor = instructor
        horario.tema = materia_texto
        horario.es_recreo = es_recreo
        color_hex = request.POST.get('color_hex')
        if color_hex:
            horario.color_hex = color_hex
        horario.save()

        messages.success(request, f"¡Clase de '{horario.nombre_materia}' actualizada correctamente!")
        return redirect(f"/academico/horarios/?nivel={nivel}&grado={grado}&seccion={seccion}")

    docentes = _docentes_activos()
    programas = ProgramaFormacion.objects.filter(activo=True).order_by('denominacion')
    aulas = [
        'Aula 101', 'Aula 102', 'Aula 103', 'Aula 104',
        'Aula 201', 'Aula 202', 'Aula 203', 'Aula 204',
        'Laboratorio de Ciencias', 'Sala de Informática 1', 'Polideportivo / Cancha'
    ]

    return render(request, 'academico/editar_horario.html', {
        'horario': horario,
        'docentes': docentes,
        'programas': programas,
        'aulas': aulas,
        'grados_por_nivel': GRADOS_POR_NIVEL,
        'secciones': SECCIONES_ESCOLARES,
        'dias': HorarioFicha.DIAS,
    })


@login_required
def nueva_matricula(request):
    alumnos = User.objects.filter(
        perfil__rol__nombre__in=['Estudiante', 'Aprendiz'],
        perfil__esta_activo=True,
    ).select_related('perfil').order_by('last_name', 'first_name')
    
    fichas = Ficha.objects.filter(estado='En Ejecucion').order_by('codigo_ficha')
    if not fichas.exists():
        fichas = Ficha.objects.all().order_by('codigo_ficha')
    grados = Matricula._meta.get_field('grado_escolar').choices
    secciones = ('A', 'B', 'C')

    alumno_preseleccionado = request.GET.get('alumno') or request.GET.get('estudiante')

    if request.method == 'POST':
        alumno_id = request.POST.get('alumno_id')
        alumno = alumnos.filter(pk=alumno_id).first()
        grado = request.POST.get('grado_escolar') or '10'
        seccion = request.POST.get('seccion') or 'A'
        
        ficha_id = request.POST.get('ficha_id')
        ficha = None
        if ficha_id:
            ficha = Ficha.objects.filter(pk=ficha_id).first()
        if not ficha:
            ficha = Ficha.objects.filter(codigo_ficha__icontains=f"{grado}-{seccion}").first() or fichas.first()

        if not alumno:
            messages.error(request, 'Por favor seleccione un estudiante de la lista.')
        elif Matricula.objects.filter(aprendiz=alumno, grado_escolar=grado, seccion=seccion, estado_formacion='En Formacion').exists():
            messages.warning(request, f'El estudiante {alumno.get_full_name()} ya se encuentra matriculado en {grado}° Sección "{seccion}".')
        else:
            mat = Matricula.objects.create(
                aprendiz=alumno,
                ficha=ficha,
                grado_escolar=grado,
                seccion=seccion,
                estado_formacion='En Formacion',
            )
            # Notificación y Auditoría
            try:
                from seguimiento.models import Notificacion, RegistroAuditoria
                Notificacion.objects.create(
                    usuario=alumno,
                    titulo="Matrícula Escolar Formalizada",
                    mensaje=f"Has sido matriculado formalmente en {mat.get_grado_escolar_display()} - Sección {seccion} para el año lectivo 2026.",
                    enlace="/matriculas/",
                    tipo="success"
                )
                for fam in alumno.nucleo_familiar.all():
                    u_fam = User.objects.filter(Q(username=fam.documento) | Q(email=fam.email)).first()
                    if u_fam:
                        Notificacion.objects.create(
                            usuario=u_fam,
                            titulo=f"Matrícula Confirmada · {alumno.first_name}",
                            mensaje=f"Se confirmó la matrícula oficial de {alumno.get_full_name()} en {mat.get_grado_escolar_display()} Sección {seccion}.",
                            enlace="/familia/matricula/",
                            tipo="success"
                        )
                RegistroAuditoria.registrar(
                    usuario=request.user,
                    modulo="Matrículas",
                    accion="Formalización de Matrícula",
                    detalles=f"Matriculó al estudiante {alumno.get_full_name()} (DNI: {getattr(alumno.perfil, 'numero_documento', 'S/D')}) en {mat.get_grado_escolar_display()} {seccion}.",
                    request=request
                )
            except Exception:
                pass

            messages.success(request, f'¡{alumno.get_full_name()} ha sido matriculado exitosamente en {mat.get_grado_escolar_display()} - Sección "{seccion}"!')
            return redirect('matriculas_lista')

    return render(request, 'academico/nueva_matricula.html', {
        'alumnos': alumnos,
        'fichas': fichas,
        'grados': grados,
        'secciones': secciones,
        'alumno_preseleccionado': alumno_preseleccionado,
    })


@login_required
def eliminar_horario(request, pk):
    horario = get_object_or_404(HorarioFicha, pk=pk)
    params = {
        'nivel': horario.nivel,
        'grado': horario.grado,
        'seccion': horario.seccion,
        'dia': horario.dia,
    }
    if request.method == 'POST':
        from usuarios.models import PapeleraReciclaje
        PapeleraReciclaje.objects.create(
            tipo_objeto='Horario',
            objeto_id=horario.id,
            titulo=f"{horario.nombre_materia} - Grado {horario.grado}°{horario.seccion}",
            subtitulo=f"{horario.get_dia_display()} {horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')} · {horario.ambiente}",
            datos_recuperacion={
                'horario_id': horario.id,
                'dia': horario.dia,
                'hora_inicio': str(horario.hora_inicio),
                'hora_fin': str(horario.hora_fin),
                'ambiente': horario.ambiente,
                'grado': horario.grado,
                'seccion': horario.seccion,
                'programa_id': horario.programa_id,
                'instructor_id': horario.instructor_id,
            },
            eliminado_por=request.user,
            motivo='Eliminado desde la gestión de horarios'
        )
        horario.activo = False
        horario.save(update_fields=['activo'])
        messages.success(request, f'Bloque "{horario.nombre_materia}" movido a la Papelera de Reciclaje.')
    return _redirigir_horarios(request, extra=params)


@login_required
def matricular_aprendiz(request, ficha_id):
    """
    Matrícula de un nuevo estudiante en una ficha técnica (RN-001, RN-002, RN-007).
    Crea el usuario, su perfil y la vinculación formal en una sola transacción segura.
    """
    ficha = get_object_or_404(Ficha, pk=ficha_id)
    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
    is_authorized = (
        request.user.is_superuser
        or request.user == ficha.instructor_lider
        or rol_nombre in ['Administrador', 'Coordinador', 'Instructor SENA', 'Instructor']
        or rol_nombre.startswith('Instructor')
        or 'inst' in request.user.username.lower()
    )
    if not is_authorized:
        messages.error(request, "No tienes autorización institucional para matricular aprendices.")
        return redirect('fichas_detalle', pk=ficha.pk)

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
from django.http import JsonResponse
from django.utils import timezone

@login_required
def api_objetivos_por_competencia(request, competencia_id):
    from .models import Objetivo
    objetivos = Objetivo.objects.filter(competencia_id=competencia_id)
    data = [{'id': o.id, 'descripcion': o.descripcion} for o in objetivos]
    return JsonResponse({'objetivos': data})

@login_required
def guardar_asistencia_clase(request):
    carga_id = request.POST.get('carga_id') or request.GET.get('carga_id')
    if request.method == 'POST' and carga_id:
        from .models import CargaAcademica, Matricula
        from seguimiento.models import AsistenciaAprendiz
        
        carga = get_object_or_404(CargaAcademica, id=carga_id, profesor=request.user)
        
        estudiantes = Matricula.objects.filter(
            grado_escolar=carga.grado,
            seccion=carga.seccion,
            estado_formacion='En Formacion'
        )
        
        hoy = timezone.localdate()
        
        for mat in estudiantes:
            estado = request.POST.get(f'asist_{mat.aprendiz.id}')
            if estado:
                AsistenciaAprendiz.objects.update_or_create(
                    matricula=mat,
                    fecha=hoy,
                    defaults={'estado': estado, 'observacion': f"Asistencia en clase: {carga.programa.denominacion if carga.programa else 'Clase'}"}
                )
        messages.success(request, f"Asistencia guardada para {carga.grado}°{carga.seccion}")
        return redirect(f"/instructor/?carga_id={carga_id}&subpanel=asistencia")
    return redirect('/instructor/?subpanel=asistencia')

@login_required
def crear_actividad_clase(request):
    if request.method == 'POST':
        from .models import CargaAcademica, Competencia, Objetivo
        from usuarios.models import EvidenciaTaller
        
        carga_id = request.POST.get('carga_id')
        carga = CargaAcademica.objects.filter(id=carga_id, profesor=request.user).first()
        if not carga:
            messages.error(request, 'No se puede asignar una tarea a una materia que no corresponde a su asignación docente.')
            return redirect('/instructor/?subpanel=actividades')
        
        competencia_id = request.POST.get('competencia_id')
        objetivo_id = request.POST.get('objetivo_id')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        fecha_limite = request.POST.get('fecha_limite')

        if fecha_limite:
            try:
                from datetime import datetime
                from django.utils import timezone
                dt_limite = timezone.make_aware(datetime.fromisoformat(fecha_limite))
                if dt_limite < timezone.now() - timezone.timedelta(minutes=5):
                    messages.error(request, 'No se puede poner una fecha límite anterior a la fecha actual.')
                    return redirect(f"/instructor/?carga_id={carga_id}&subpanel=actividades")
            except Exception:
                pass
        
        EvidenciaTaller.objects.create(
            instructor=request.user,
            competencia_id=competencia_id,
            objetivo_id=objetivo_id,
            titulo=titulo,
            descripcion=descripcion,
            fecha_limite=fecha_limite
        )
        messages.success(request, f"Actividad '{titulo}' asignada exitosamente al grupo {carga.grado}°{carga.seccion}.")
        return redirect(f"/instructor/?carga_id={carga_id}&subpanel=actividades")
    return redirect('/instructor/?subpanel=actividades')

@login_required
def horarios_cambiar_color(request):
    if request.method == 'POST':
        horario_id = request.POST.get('horario_id')
        color_clase = request.POST.get('color_clase')
        
        from .models import HorarioFicha
        horario = get_object_or_404(HorarioFicha, id=horario_id)
        horario.color_hex = color_clase
        horario.save()
        
        messages.success(request, f"Color de clase actualizado exitosamente.")
    return redirect('horarios_tablero')
