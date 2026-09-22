from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from .models import InstitucionEducativa, ContactoInstitucional, ObservacionInstitucional
from .forms import InstitucionEducativaForm, ContactoInstitucionalForm, ObservacionInstitucionalForm
from seguimiento.models import RegistroAuditoria, SeguimientoAdministrativo, DocumentoAdministrativo, BitacoraSeguimiento
from convenios.models import ConvenioSENA
from academico.models import Matricula, ProgramaFormacion
from usuarios.decorators import requerir_roles
from django.contrib.auth.models import User


@login_required
def lista_instituciones(request):
    """
    Directorio interactivo de Instituciones Educativas con buscador reactivo,
    KPIs en tiempo real, filtros avanzados, ordenamiento y paginación.
    """
    # 1. KPIs Globales
    total_instituciones = InstitucionEducativa.objects.count()
    total_activas = InstitucionEducativa.objects.filter(activa=True).count()
    total_inactivas = InstitucionEducativa.objects.filter(activa=False).count()
    con_fichas = InstitucionEducativa.objects.filter(fichas__isnull=False).distinct().count()
    sin_fichas = InstitucionEducativa.objects.filter(fichas__isnull=True).distinct().count()

    # 2. Captura de Parámetros
    query = request.GET.get('q', '').strip()
    municipio_filtro = request.GET.get('municipio', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()
    fichas_filtro = request.GET.get('fichas', '').strip()
    orden = request.GET.get('orden', 'nombre_asc').strip()

    # 3. Construcción del Queryset con conteos
    instituciones = InstitucionEducativa.objects.annotate(
        num_fichas=Count('fichas', distinct=True),
        num_aprendices=Count('fichas__matriculas', distinct=True)
    )

    if query:
        instituciones = instituciones.filter(
            Q(nombre__icontains=query) |
            Q(codigo_dane__icontains=query) |
            Q(rector_nombre__icontains=query) |
            Q(municipio__icontains=query)
        )

    if municipio_filtro:
        instituciones = instituciones.filter(municipio__iexact=municipio_filtro)

    if estado_filtro == 'activas':
        instituciones = instituciones.filter(activa=True)
    elif estado_filtro == 'inactivas':
        instituciones = instituciones.filter(activa=False)

    if fichas_filtro == 'con_fichas':
        instituciones = instituciones.filter(num_fichas__gt=0)
    elif fichas_filtro == 'sin_fichas':
        instituciones = instituciones.filter(num_fichas=0)

    # 4. Ordenamiento
    if orden == 'nombre_desc':
        instituciones = instituciones.order_by('-nombre')
    elif orden == 'fichas_desc':
        instituciones = instituciones.order_by('-num_fichas', 'nombre')
    elif orden == 'recientes':
        instituciones = instituciones.order_by('-id')
    else:  # nombre_asc por defecto
        instituciones = instituciones.order_by('nombre')

    # 5. Paginación (10 por página)
    paginator = Paginator(instituciones, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Municipios únicos para el selector
    municipios = InstitucionEducativa.objects.values_list('municipio', flat=True).distinct().order_by('municipio')

    # Listas completas para despliegue interactivo en cada tarjeta KPI
    colegios_todos = InstitucionEducativa.objects.annotate(
        num_fichas=Count('fichas', distinct=True)
    ).order_by('nombre')
    colegios_activas = colegios_todos.filter(activa=True)
    colegios_inactivas = colegios_todos.filter(activa=False)
    colegios_con_fichas = colegios_todos.filter(num_fichas__gt=0)
    colegios_sin_fichas = colegios_todos.filter(num_fichas=0)

    context = {
        'page_obj': page_obj,
        'instituciones': page_obj,
        'total_instituciones': total_instituciones,
        'total_activas': total_activas,
        'total_inactivas': total_inactivas,
        'con_fichas': con_fichas,
        'sin_fichas': sin_fichas,
        'colegios_todos': colegios_todos,
        'colegios_activas': colegios_activas,
        'colegios_inactivas': colegios_inactivas,
        'colegios_con_fichas': colegios_con_fichas,
        'colegios_sin_fichas': colegios_sin_fichas,
        'query': query,
        'municipio_filtro': municipio_filtro,
        'estado_filtro': estado_filtro,
        'fichas_filtro': fichas_filtro,
        'orden': orden,
        'municipios': municipios,
    }
    return render(request, 'instituciones/lista.html', context)


@login_required
def detalle_institucion(request, pk):
    """
    Perfil Institucional Completo del Colegio con 9 Pestañas 100% Funcionales:
    1. Información General
    2. Convenios SENA (alertas, beneficios, vencimientos)
    3. Programas Articulados (con enlace al Semáforo)
    4. Contactos Institucionales (Rector, Coordinador, Enlaces)
    5. Documentos Administrativos (Subida y descarga real)
    6. Seguimientos Administrativos (Prioridades y estados)
    7. Observaciones (Reuniones, acuerdos, visitas)
    8. Antecedentes Institucionales
    9. Historial de Auditoría
    """
    institucion = get_object_or_404(InstitucionEducativa, pk=pk)

    # Manejo de Acciones POST directamente desde las pestañas y modales
    if request.method == 'POST':
        accion = request.POST.get('accion')

        # 1. Crear Contacto desde pestaña
        if accion == 'crear_contacto':
            nom = request.POST.get('nombre', '').strip()
            ape = request.POST.get('apellido', '').strip()
            cargo = request.POST.get('cargo', '').strip()
            tipo = request.POST.get('tipo', 'Coordinador')
            correo = request.POST.get('correo', '').strip()
            tel = request.POST.get('telefono', '').strip()
            obs = request.POST.get('observaciones', '').strip()
            if nom and cargo:
                ContactoInstitucional.objects.create(
                    institucion=institucion,
                    nombre=nom,
                    apellido=ape,
                    cargo=cargo,
                    tipo=tipo,
                    correo=correo,
                    telefono=tel,
                    observaciones=obs,
                    estado='Activo'
                )
                RegistroAuditoria.registrar(
                    usuario=request.user,
                    modulo='Contactos',
                    accion='Creación de Contacto',
                    detalles=f"Se vinculó el contacto '{nom} {ape}' ({cargo}) en {institucion.nombre}.",
                    request=request
                )
                messages.success(request, f"Contacto '{nom} {ape}' registrado exitosamente.")
            else:
                messages.error(request, "Nombre y cargo son obligatorios para el contacto.")
            return redirect(f"/instituciones/{institucion.id}/?tab=contactos")

        # 2. Crear Observación / Antecedente desde pestaña
        elif accion == 'crear_observacion':
            tit = request.POST.get('titulo', '').strip()
            tip = request.POST.get('tipo', 'Reunión')
            prio = request.POST.get('prioridad', 'Media')
            desc = request.POST.get('descripcion', '').strip()
            res = request.POST.get('resultado', '').strip()
            f_seg = request.POST.get('fecha_seguimiento') or None
            conv_id = request.POST.get('convenio')
            conv_obj = ConvenioSENA.objects.filter(pk=conv_id).first() if conv_id else None

            if tit and desc:
                ObservacionInstitucional.objects.create(
                    institucion=institucion,
                    convenio=conv_obj,
                    titulo=tit,
                    tipo=tip,
                    prioridad=prio,
                    descripcion=desc,
                    resultado=res,
                    responsable=request.user,
                    fecha_seguimiento=f_seg,
                    estado='Pendiente'
                )
                RegistroAuditoria.registrar(
                    usuario=request.user,
                    modulo='Observaciones',
                    accion='Registro de Observación',
                    detalles=f"Se registró '{tit}' ({tip}) para {institucion.nombre}.",
                    request=request
                )
                messages.success(request, f"Observación '{tit}' registrada correctamente.")
            else:
                messages.error(request, "El título y la descripción son obligatorios.")
            destino_tab = 'antecedentes' if tip == 'Antecedente' else 'observaciones'
            return redirect(f"/instituciones/{institucion.id}/?tab={destino_tab}")

        # 3. Crear Seguimiento Administrativo desde pestaña
        elif accion == 'crear_seguimiento':
            asunto = request.POST.get('asunto', '').strip()
            desc = request.POST.get('descripcion', '').strip()
            prio = request.POST.get('prioridad', 'Media')
            f_lim = request.POST.get('fecha_limite') or None
            conv_id = request.POST.get('convenio')
            conv_obj = ConvenioSENA.objects.filter(pk=conv_id).first() if conv_id else None

            if asunto and desc:
                SeguimientoAdministrativo.objects.create(
                    institucion=institucion,
                    convenio=conv_obj,
                    responsable=request.user,
                    asunto=asunto,
                    descripcion=desc,
                    prioridad=prio,
                    fecha_limite=f_lim,
                    estado='Pendiente'
                )
                RegistroAuditoria.registrar(
                    usuario=request.user,
                    modulo='Seguimientos',
                    accion='Creación de Seguimiento',
                    detalles=f"Se creó seguimiento administrativo '{asunto}' en {institucion.nombre}.",
                    request=request
                )
                messages.success(request, f"Seguimiento '{asunto}' creado correctamente.")
            else:
                messages.error(request, "El asunto y la descripción son obligatorios.")
            return redirect(f"/instituciones/{institucion.id}/?tab=seguimientos")

        # 4. Subir Documento Administrativo desde pestaña
        elif accion == 'subir_documento':
            nombre_doc = request.POST.get('nombre', '').strip()
            tipo_doc = request.POST.get('tipo', 'Acta')
            desc = request.POST.get('descripcion', '').strip()
            archivo = request.FILES.get('archivo')
            conv_id = request.POST.get('convenio')
            conv_obj = ConvenioSENA.objects.filter(pk=conv_id).first() if conv_id else None

            if nombre_doc and archivo:
                DocumentoAdministrativo.objects.create(
                    institucion=institucion,
                    convenio=conv_obj,
                    nombre=nombre_doc,
                    tipo=tipo_doc,
                    descripcion=desc,
                    archivo=archivo,
                    subido_por=request.user
                )
                RegistroAuditoria.registrar(
                    usuario=request.user,
                    modulo='Documentos',
                    accion='Carga de Documento',
                    detalles=f"Se subió documento '{nombre_doc}' ({tipo_doc}) en {institucion.nombre}.",
                    request=request
                )
                messages.success(request, f"Documento '{nombre_doc}' subido exitosamente.")
            else:
                messages.error(request, "Debes ingresar un nombre y seleccionar un archivo válido.")
            return redirect(f"/instituciones/{institucion.id}/?tab=documentos")

        # 5. Cambiar Estado de Seguimiento
        elif accion == 'cambiar_estado_seguimiento':
            seg_id = request.POST.get('seguimiento_id')
            nuevo_est = request.POST.get('nuevo_estado')
            seg = get_object_or_404(SeguimientoAdministrativo, pk=seg_id, institucion=institucion)
            seg.estado = nuevo_est
            seg.save()
            messages.success(request, f"Seguimiento '{seg.asunto}' actualizado a estado {nuevo_est}.")
            return redirect(f"/instituciones/{institucion.id}/?tab=seguimientos")

    # Consultas para las 9 Pestañas
    tab_activa = request.GET.get('tab', 'general').strip()

    # 1. Convenios
    convenios_colegio = ConvenioSENA.objects.filter(
        Q(institucion_educativa=institucion) |
        Q(institucion__codigo_dane=institucion.codigo_dane) |
        Q(institucion__nombre__icontains=institucion.nombre) |
        Q(nombre__icontains=institucion.nombre)
    ).distinct().prefetch_related('beneficios', 'documentos').order_by('-fecha_fin')

    # 2. Programas y Fichas
    fichas = institucion.fichas.select_related('programa', 'instructor_lider').order_by('-fecha_inicio')
    programas_colegio = ProgramaFormacion.objects.filter(
        Q(institucion=institucion) | Q(fichas__institucion=institucion)
    ).distinct().order_by('denominacion')

    # 3. Contactos
    contactos = ContactoInstitucional.objects.filter(institucion=institucion).order_by('apellido', 'nombre')

    # 4. Documentos
    documentos_colegio = DocumentoAdministrativo.objects.filter(
        Q(institucion=institucion) | Q(convenio__in=convenios_colegio)
    ).distinct().select_related('subido_por').order_by('-fecha_subida')

    # 5. Seguimientos Administrativos
    seguimientos_admin = SeguimientoAdministrativo.objects.filter(
        institucion=institucion
    ).select_related('responsable', 'convenio').order_by('-fecha_limite', '-fecha_registro')

    # 6. Observaciones (excluyendo antecedentes formales)
    observaciones_colegio = ObservacionInstitucional.objects.filter(
        institucion=institucion
    ).exclude(tipo='Antecedente').select_related('responsable', 'convenio').order_by('-fecha', '-fecha_registro')

    # 7. Antecedentes Institucionales
    antecedentes_colegio = ObservacionInstitucional.objects.filter(
        institucion=institucion, tipo='Antecedente'
    ).select_related('responsable', 'convenio').order_by('-fecha')

    # 8. Historial de Auditoría
    historial = RegistroAuditoria.objects.filter(
        Q(detalles__icontains=institucion.codigo_dane) |
        Q(detalles__icontains=institucion.nombre)
    ).select_related('usuario').order_by('-fecha')[:25]

    # Estadísticas del Colegio
    f_ids = fichas.values_list('id', flat=True)
    total_aprendices = Matricula.objects.filter(ficha__in=f_ids).count()
    total_instructores = User.objects.filter(
        Q(fichas_asignadas__institucion=institucion) |
        Q(seguimientos_registrados__ficha__institucion=institucion)
    ).distinct().count()

    context = {
        'institucion': institucion,
        'tab_activa': tab_activa,
        'convenios_colegio': convenios_colegio,
        'total_convenios': convenios_colegio.count(),
        'fichas': fichas,
        'total_fichas': fichas.count(),
        'programas_colegio': programas_colegio,
        'total_programas': programas_colegio.count(),
        'contactos': contactos,
        'total_contactos': contactos.count(),
        'documentos_colegio': documentos_colegio,
        'total_documentos': documentos_colegio.count(),
        'seguimientos_admin': seguimientos_admin,
        'total_seguimientos': seguimientos_admin.count(),
        'observaciones_colegio': observaciones_colegio,
        'total_observaciones': observaciones_colegio.count(),
        'antecedentes_colegio': antecedentes_colegio,
        'total_antecedentes': antecedentes_colegio.count(),
        'historial': historial,
        'total_aprendices': total_aprendices,
        'total_instructores': total_instructores,
    }
    return render(request, 'instituciones/detalle.html', context)


@login_required
def crear_institucion(request):
    """
    Registro de una nueva institución educativa en convenio con trazabilidad en auditoría.
    """
    if request.method == 'POST':
        form = InstitucionEducativaForm(request.POST)
        if form.is_valid():
            colegio = form.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Instituciones',
                accion='Registro de Nueva Institución',
                detalles=f"Se vinculó la institución educativa '{colegio.nombre}' (DANE: {colegio.codigo_dane}) en {colegio.municipio}.",
                request=request
            )
            messages.success(request, f"Colegio '{colegio.nombre}' registrado exitosamente en SINETEC.")
            return redirect('instituciones_detalle', pk=colegio.pk)
        else:
            messages.error(request, "Por favor corrija los errores marcados en el formulario.")
    else:
        form = InstitucionEducativaForm()

    return render(request, 'instituciones/formulario.html', {'form': form, 'titulo': 'Registrar Nueva Institución Educativa'})


@login_required
def editar_institucion(request, pk):
    """
    Edición de datos de una institución educativa existente con trazabilidad en auditoría.
    """
    institucion = get_object_or_404(InstitucionEducativa, pk=pk)
    if request.method == 'POST':
        form = InstitucionEducativaForm(request.POST, instance=institucion)
        if form.is_valid():
            form.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Instituciones',
                accion='Edición de Institución',
                detalles=f"Se actualizaron los datos del colegio '{institucion.nombre}' (DANE: {institucion.codigo_dane}).",
                request=request
            )
            messages.success(request, f"Datos del colegio '{institucion.nombre}' actualizados correctamente.")
            return redirect('instituciones_detalle', pk=institucion.pk)
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = InstitucionEducativaForm(instance=institucion)

    return render(request, 'instituciones/formulario.html', {'form': form, 'titulo': 'Editar Institución Educativa', 'institucion': institucion})


@login_required
def cambiar_estado_institucion(request, pk):
    """
    Alterna de forma segura el estado de una institución (Activa / Inactiva) con auditoría.
    """
    institucion = get_object_or_404(InstitucionEducativa, pk=pk)
    institucion.activa = not institucion.activa
    institucion.save()

    nuevo_estado = "Activa" if institucion.activa else "Inactiva"
    RegistroAuditoria.registrar(
        usuario=request.user,
        modulo='Instituciones',
        accion=f'Cambio de Estado a {nuevo_estado}',
        detalles=f"Se modificó el estado del colegio '{institucion.nombre}' (DANE: {institucion.codigo_dane}) a {nuevo_estado}.",
        request=request
    )
    messages.success(request, f"La institución '{institucion.nombre}' ahora está marcada como {nuevo_estado}.")

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('instituciones_detalle', pk=institucion.pk)


@login_required
def eliminar_institucion(request, pk):
    """
    Eliminación segura de una institución educativa:
    Si posee fichas técnicas vinculadas, se rechaza la eliminación destructiva
    y se instruye al usuario a desactivarla para mantener la integridad referencial.
    """
    institucion = get_object_or_404(InstitucionEducativa, pk=pk)
    fichas_count = institucion.fichas.count()

    if fichas_count > 0:
        messages.warning(
            request,
            f"No es posible eliminar '{institucion.nombre}' porque tiene {fichas_count} ficha(s) técnica(s) asociada(s). "
            f"Para suspender las operaciones con este plantel, cambie su estado a 'Inactiva'."
        )
        return redirect('instituciones_detalle', pk=institucion.pk)

    if request.method == 'POST':
        nombre = institucion.nombre
        dane = institucion.codigo_dane
        institucion.delete()
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Instituciones',
            accion='Eliminación de Institución',
            detalles=f"Se eliminó la institución educativa '{nombre}' (DANE: {dane}) del sistema.",
            request=request
        )
        messages.success(request, f"La institución '{nombre}' ha sido eliminada del sistema.")
        return redirect('instituciones_lista')

    return render(request, 'instituciones/confirmar_eliminar.html', {'institucion': institucion})


# ==============================================================================
# MÓDULO CONTACTOS INSTITUCIONALES (RECTORES, COORDINADORES, ENLACES)
# ==============================================================================

@login_required
def contactos_lista(request):
    """
    Catálogo general de contactos institucionales de colegios articulados con el SENA.
    Buscador rápido, filtros por colegio, tipo y estado, ordenamiento y comunicación directa.
    """
    query = request.GET.get('q', '').strip()
    colegio_filtro = request.GET.get('colegio', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    contactos = ContactoInstitucional.objects.select_related('institucion').order_by('institucion__nombre', 'apellido')

    if query:
        contactos = contactos.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(cargo__icontains=query) |
            Q(correo__icontains=query) |
            Q(telefono__icontains=query) |
            Q(institucion__nombre__icontains=query)
        )

    if colegio_filtro:
        contactos = contactos.filter(institucion_id=colegio_filtro)

    if tipo_filtro:
        contactos = contactos.filter(tipo=tipo_filtro)

    if estado_filtro:
        contactos = contactos.filter(estado=estado_filtro)

    # Métricas
    total_contactos = ContactoInstitucional.objects.count()
    total_activos = ContactoInstitucional.objects.filter(estado='Activo').count()
    total_rectores = ContactoInstitucional.objects.filter(tipo='Rector').count()
    total_enlaces = ContactoInstitucional.objects.filter(tipo__in=['Coordinador', 'Docente Enlace']).count()

    paginator = Paginator(contactos, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    colegios = InstitucionEducativa.objects.order_by('nombre')
    tipos_contacto = ContactoInstitucional.TIPO_CHOICES

    context = {
        'page_obj': page_obj,
        'contactos': page_obj,
        'total_contactos': total_contactos,
        'total_activos': total_activos,
        'total_rectores': total_rectores,
        'total_enlaces': total_enlaces,
        'colegios': colegios,
        'tipos_contacto': tipos_contacto,
        'query': query,
        'colegio_filtro': colegio_filtro,
        'tipo_filtro': tipo_filtro,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'instituciones/contactos_lista.html', context)


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría')
def contacto_crear(request):
    """
    Creación formal de un nuevo contacto institucional.
    """
    institucion_previa = request.GET.get('institucion')
    if request.method == 'POST':
        form = ContactoInstitucionalForm(request.POST)
        if form.is_valid():
            contacto = form.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Contactos',
                accion='Creación de Contacto',
                detalles=f"Se creó el contacto '{contacto.nombre_completo}' ({contacto.cargo}) en {contacto.institucion.nombre}.",
                request=request
            )
            messages.success(request, f"Contacto '{contacto.nombre_completo}' registrado exitosamente.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('contactos_lista')
        else:
            messages.error(request, "Por favor corrija los errores marcados en el formulario.")
    else:
        initial = {'institucion': institucion_previa} if institucion_previa else {}
        form = ContactoInstitucionalForm(initial=initial)

    return render(request, 'instituciones/contacto_formulario.html', {'form': form, 'titulo': 'Registrar Contacto Institucional'})


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría')
def contacto_editar(request, pk):
    """
    Edición de datos de un contacto institucional existente.
    """
    contacto = get_object_or_404(ContactoInstitucional, pk=pk)
    if request.method == 'POST':
        form = ContactoInstitucionalForm(request.POST, instance=contacto)
        if form.is_valid():
            contacto = form.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Contactos',
                accion='Edición de Contacto',
                detalles=f"Se actualizaron los datos del contacto '{contacto.nombre_completo}' ({contacto.cargo}).",
                request=request
            )
            messages.success(request, f"Contacto '{contacto.nombre_completo}' actualizado correctamente.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('contactos_lista')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ContactoInstitucionalForm(instance=contacto)

    return render(request, 'instituciones/contacto_formulario.html', {'form': form, 'titulo': 'Editar Contacto Institucional', 'contacto': contacto})


@login_required
@requerir_roles('Administrador', 'Coordinador')
def contacto_eliminar(request, pk):
    """
    Eliminación segura de un contacto institucional.
    """
    contacto = get_object_or_404(ContactoInstitucional, pk=pk)
    if request.method == 'POST':
        nom = contacto.nombre_completo
        col = contacto.institucion.nombre
        contacto.delete()
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Contactos',
            accion='Eliminación de Contacto',
            detalles=f"Se eliminó el contacto '{nom}' de la institución {col}.",
            request=request
        )
        messages.success(request, f"Contacto '{nom}' eliminado del sistema.")
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('contactos_lista')

    return render(request, 'instituciones/confirmar_eliminar_contacto.html', {'contacto': contacto})


# ==============================================================================
# MÓDULO OBSERVACIONES Y ANTECEDENTES INSTITUCIONALES
# ==============================================================================

@login_required
def observaciones_lista(request):
    """
    Directorio administrativo de Observaciones, Reuniones, Acuerdos y Antecedentes
    registrados para todas las instituciones educativas articuladas.
    """
    query = request.GET.get('q', '').strip()
    colegio_filtro = request.GET.get('colegio', '').strip()
    tipo_filtro = request.GET.get('tipo', '').strip()
    prioridad_filtro = request.GET.get('prioridad', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    observaciones = ObservacionInstitucional.objects.select_related('institucion', 'convenio', 'responsable').order_by('-fecha', '-fecha_registro')

    if query:
        observaciones = observaciones.filter(
            Q(titulo__icontains=query) |
            Q(descripcion__icontains=query) |
            Q(resultado__icontains=query) |
            Q(institucion__nombre__icontains=query)
        )

    if colegio_filtro:
        observaciones = observaciones.filter(institucion_id=colegio_filtro)

    if tipo_filtro:
        observaciones = observaciones.filter(tipo=tipo_filtro)

    if prioridad_filtro:
        observaciones = observaciones.filter(prioridad=prioridad_filtro)

    if estado_filtro:
        observaciones = observaciones.filter(estado=estado_filtro)

    # Indicadores
    total_observaciones = ObservacionInstitucional.objects.count()
    total_pendientes = ObservacionInstitucional.objects.filter(estado='Pendiente').count()
    total_en_proceso = ObservacionInstitucional.objects.filter(estado='En Proceso').count()
    total_urgentes = ObservacionInstitucional.objects.filter(prioridad='Urgente').count()

    paginator = Paginator(observaciones, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    colegios = InstitucionEducativa.objects.order_by('nombre')
    tipos_obs = ObservacionInstitucional.TIPO_CHOICES
    prioridades = ObservacionInstitucional.PRIORIDAD_CHOICES
    estados = ObservacionInstitucional.ESTADO_CHOICES

    context = {
        'page_obj': page_obj,
        'observaciones': page_obj,
        'total_observaciones': total_observaciones,
        'total_pendientes': total_pendientes,
        'total_en_proceso': total_en_proceso,
        'total_urgentes': total_urgentes,
        'colegios': colegios,
        'tipos_obs': tipos_obs,
        'prioridades': prioridades,
        'estados': estados,
        'query': query,
        'colegio_filtro': colegio_filtro,
        'tipo_filtro': tipo_filtro,
        'prioridad_filtro': prioridad_filtro,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'instituciones/observaciones_lista.html', context)


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría', 'Instructor SENA')
def observacion_crear(request):
    """
    Registro formal de una nueva observación, reunión, acuerdo o antecedente institucional.
    """
    institucion_previa = request.GET.get('institucion')
    tipo_previo = request.GET.get('tipo', 'Reunión')
    if request.method == 'POST':
        form = ObservacionInstitucionalForm(request.POST)
        if form.is_valid():
            obs = form.save(commit=False)
            obs.responsable = request.user
            obs.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Observaciones',
                accion='Registro de Observación',
                detalles=f"Se registró '{obs.titulo}' ({obs.tipo}) en {obs.institucion.nombre}.",
                request=request
            )
            messages.success(request, f"Observación '{obs.titulo}' guardada exitosamente.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('observaciones_lista')
        else:
            messages.error(request, "Por favor corrija los errores marcados en el formulario.")
    else:
        initial = {'institucion': institucion_previa, 'tipo': tipo_previo, 'fecha': timezone.localdate()}
        form = ObservacionInstitucionalForm(initial=initial)

    return render(request, 'instituciones/observacion_formulario.html', {'form': form, 'titulo': 'Registrar Observación / Antecedente'})


@login_required
@requerir_roles('Administrador', 'Coordinador', 'Secretaría')
def observacion_editar(request, pk):
    """
    Edición de una observación o antecedente existente.
    """
    obs = get_object_or_404(ObservacionInstitucional, pk=pk)
    if request.method == 'POST':
        form = ObservacionInstitucionalForm(request.POST, instance=obs)
        if form.is_valid():
            obs = form.save()
            RegistroAuditoria.registrar(
                usuario=request.user,
                modulo='Observaciones',
                accion='Edición de Observación',
                detalles=f"Se actualizó '{obs.titulo}' ({obs.tipo}) de {obs.institucion.nombre}.",
                request=request
            )
            messages.success(request, f"Observación '{obs.titulo}' actualizada correctamente.")
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('observaciones_lista')
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = ObservacionInstitucionalForm(instance=obs)

    return render(request, 'instituciones/observacion_formulario.html', {'form': form, 'titulo': 'Editar Observación / Antecedente', 'observacion': obs})


@login_required
@requerir_roles('Administrador', 'Coordinador')
def observacion_eliminar(request, pk):
    """
    Eliminación de una observación o antecedente.
    """
    obs = get_object_or_404(ObservacionInstitucional, pk=pk)
    if request.method == 'POST':
        tit = obs.titulo
        col = obs.institucion.nombre
        obs.delete()
        RegistroAuditoria.registrar(
            usuario=request.user,
            modulo='Observaciones',
            accion='Eliminación de Observación',
            detalles=f"Se eliminó '{tit}' de la institución {col}.",
            request=request
        )
        messages.success(request, f"Observación '{tit}' eliminada correctamente.")
        next_url = request.GET.get('next') or request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('observaciones_lista')

    return render(request, 'instituciones/confirmar_eliminar_observacion.html', {'observacion': obs})
