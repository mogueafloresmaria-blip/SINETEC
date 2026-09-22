import os
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, Http404
from django.utils import timezone
from django.db.models import Q

from .models import InstitucionConvenio, ConvenioSENA, DocumentoConvenio, BeneficioConvenio
from .forms import InstitucionConvenioForm, ConvenioSENAForm, DocumentoConvenioForm, BeneficioConvenioForm



def _user_can_manage_convenios(user):
    """Verifica si el usuario tiene permisos administrativos para gestionar convenios SENA."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.is_staff:
        return True
    
    # Comprobar rol de SINETEC si existe
    if hasattr(user, 'perfil') and user.perfil.rol:
        rol_nombre = user.perfil.rol.nombre.lower()
        if any(r in rol_nombre for r in ['admin', 'coordinador', 'rector', 'secretaria', 'director']):
            return True
    return False


@login_required
def catalogo_convenios(request):
    """
    Página principal del catálogo visual de Instituciones y Convenios SENA.
    Incluye estadísticas calculadas en tiempo real y buscador multifiltro.
    """
    can_manage = _user_can_manage_convenios(request.user)
    
    # Obtener parámetros de búsqueda y filtrado
    q = request.GET.get('q', '').strip()
    filtro_estado = request.GET.get('estado', '').strip()
    filtro_municipio = request.GET.get('municipio', '').strip()
    filtro_tipo = request.GET.get('tipo', '').strip()

    # Queryset base: Instituciones activas por defecto (salvo que se busque inactivas)
    instituciones_qs = InstitucionConvenio.objects.filter(activo=True).prefetch_related('convenios', 'convenios__documentos')

    # Búsqueda por texto libre
    if q:
        instituciones_qs = instituciones_qs.filter(
            Q(nombre__icontains=q) |
            Q(municipio__icontains=q) |
            Q(codigo_dane__icontains=q) |
            Q(convenios__numero_convenio__icontains=q) |
            Q(convenios__nombre__icontains=q)
        ).distinct()

    # Filtro por municipio
    if filtro_municipio:
        instituciones_qs = instituciones_qs.filter(municipio__iexact=filtro_municipio)

    # Filtro por tipo de convenio
    if filtro_tipo:
        instituciones_qs = instituciones_qs.filter(convenios__tipo_convenio=filtro_tipo).distinct()

    # Filtrar por estado dinámico si se solicita
    instituciones_lista = list(instituciones_qs)
    if filtro_estado:
        instituciones_lista = [
            inst for inst in instituciones_lista
            if inst.estado_convenio_resumen.lower() == filtro_estado.lower()
        ]

    # Estadísticas globales extraídas directamente de la base de datos
    todos_convenios = ConvenioSENA.objects.select_related('institucion').all()
    total_instituciones = InstitucionConvenio.objects.filter(activo=True).count()
    
    total_activos = 0
    total_proximos = 0
    total_vencidos = 0
    
    for conv in todos_convenios:
        st = conv.estado
        if st == 'Activo':
            total_activos += 1
        elif st == 'Próximo a vencer':
            total_proximos += 1
        elif st == 'Vencido':
            total_vencidos += 1

    # Opciones dinámicas para los selects de filtro
    municipios_disponibles = InstitucionConvenio.objects.filter(activo=True).values_list('municipio', flat=True).distinct().order_by('municipio')
    tipos_disponibles = ConvenioSENA.TIPO_CHOICES

    context = {
        'instituciones': instituciones_lista,
        'total_instituciones': total_instituciones,
        'total_activos': total_activos,
        'total_proximos': total_proximos,
        'total_vencidos': total_vencidos,
        'municipios_disponibles': municipios_disponibles,
        'tipos_disponibles': tipos_disponibles,
        'filtro_q': q,
        'filtro_estado': filtro_estado,
        'filtro_municipio': filtro_municipio,
        'filtro_tipo': filtro_tipo,
        'can_manage': can_manage,
    }
    return render(request, 'convenios/catalogo.html', context)


@login_required
def institucion_detalle(request, pk):
    """
    Vista detallada de la institución educativa, sus convenios SENA y documentos asociados.
    """
    institucion = get_object_or_404(InstitucionConvenio.objects.prefetch_related('convenios__documentos__usuario_carga'), pk=pk)
    can_manage = _user_can_manage_convenios(request.user)
    convenios = institucion.convenios.all()

    context = {
        'institucion': institucion,
        'convenios': convenios,
        'can_manage': can_manage,
    }
    return render(request, 'convenios/institucion_detalle.html', context)


@login_required
def institucion_crear(request):
    """Registrar nueva institución educativa para catálogo de convenios."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para registrar instituciones.")

    if request.method == 'POST':
        form = InstitucionConvenioForm(request.POST, request.FILES)
        if form.is_valid():
            inst = form.save()
            messages.success(request, f"Institución '{inst.nombre}' registrada exitosamente.")
            return redirect('institucion_convenio_detalle', pk=inst.pk)
    else:
        form = InstitucionConvenioForm()

    return render(request, 'convenios/institucion_formulario.html', {
        'form': form,
        'titulo': 'Registrar Nueva Institución Educativa',
        'boton_texto': 'Guardar Institución'
    })


@login_required
def institucion_editar(request, pk):
    """Editar información de una institución educativa."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para editar instituciones.")

    institucion = get_object_or_404(InstitucionConvenio, pk=pk)
    if request.method == 'POST':
        form = InstitucionConvenioForm(request.POST, request.FILES, instance=institucion)
        if form.is_valid():
            inst = form.save()
            messages.success(request, f"Institución '{inst.nombre}' actualizada exitosamente.")
            return redirect('institucion_convenio_detalle', pk=inst.pk)
    else:
        form = InstitucionConvenioForm(instance=institucion)

    return render(request, 'convenios/institucion_formulario.html', {
        'form': form,
        'institucion': institucion,
        'titulo': f'Editar Institución: {institucion.nombre}',
        'boton_texto': 'Guardar Cambios'
    })


@login_required
def institucion_desactivar(request, pk):
    """Borrado lógico de la institución (desactivar sin eliminar registros históricos)."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para desactivar instituciones.")

    institucion = get_object_or_404(InstitucionConvenio, pk=pk)
    if request.method == 'POST':
        institucion.activo = not institucion.activo
        institucion.save()
        estado_str = "activada" if institucion.activo else "desactivada"
        messages.info(request, f"La institución '{institucion.nombre}' ha sido {estado_str} correctamente.")
        return redirect('convenios_catalogo')
    
    return render(request, 'convenios/confirmar_desactivar.html', {
        'institucion': institucion
    })


@login_required
def convenio_crear(request, institucion_id=None):
    """Crear un nuevo Convenio SENA asociado a una institución."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para crear convenios.")

    institucion_preseleccionada = None
    if institucion_id:
        institucion_preseleccionada = get_object_or_404(InstitucionConvenio, pk=institucion_id)

    if request.method == 'POST':
        form = ConvenioSENAForm(request.POST)
        if form.is_valid():
            conv = form.save()
            messages.success(request, f"Convenio '{conv.numero_convenio}' creado exitosamente para {conv.institucion.nombre}.")
            return redirect('institucion_convenio_detalle', pk=conv.institucion.pk)
    else:
        initial_data = {}
        if institucion_preseleccionada:
            initial_data['institucion'] = institucion_preseleccionada
        form = ConvenioSENAForm(initial=initial_data)

    return render(request, 'convenios/convenio_formulario.html', {
        'form': form,
        'institucion': institucion_preseleccionada,
        'titulo': 'Nuevo Convenio SENA',
        'boton_texto': 'Registrar Convenio'
    })


@login_required
def convenio_editar(request, pk):
    """Editar información de un Convenio SENA existente."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para editar convenios.")

    convenio = get_object_or_404(ConvenioSENA, pk=pk)
    if request.method == 'POST':
        form = ConvenioSENAForm(request.POST, instance=convenio)
        if form.is_valid():
            conv = form.save()
            messages.success(request, f"Convenio '{conv.numero_convenio}' actualizado exitosamente.")
            return redirect('institucion_convenio_detalle', pk=conv.institucion.pk)
    else:
        form = ConvenioSENAForm(instance=convenio)

    return render(request, 'convenios/convenio_formulario.html', {
        'form': form,
        'convenio': convenio,
        'institucion': convenio.institucion,
        'titulo': f'Editar Convenio: {convenio.numero_convenio}',
        'boton_texto': 'Guardar Cambios'
    })


@login_required
def convenio_eliminar(request, pk):
    """Eliminación de un convenio SENA."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para eliminar convenios.")

    convenio = get_object_or_404(ConvenioSENA, pk=pk)
    inst_id = convenio.institucion.pk
    if request.method == 'POST':
        num = convenio.numero_convenio
        convenio.delete()
        messages.warning(request, f"El convenio '{num}' ha sido eliminado.")
        return redirect('institucion_convenio_detalle', pk=inst_id)

    return render(request, 'convenios/confirmar_eliminar_convenio.html', {
        'convenio': convenio
    })


@login_required
def documento_subir(request, convenio_id):
    """Subir un documento o anexo legal al convenio SENA usando Django storage real."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para cargar documentos.")

    convenio = get_object_or_404(ConvenioSENA, pk=convenio_id)
    if request.method == 'POST':
        form = DocumentoConvenioForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.convenio = convenio
            doc.usuario_carga = request.user
            doc.save()
            messages.success(request, f"Documento '{doc.nombre}' cargado correctamente.")
            return redirect('institucion_convenio_detalle', pk=convenio.institucion.pk)
    else:
        form = DocumentoConvenioForm()

    return render(request, 'convenios/documento_formulario.html', {
        'form': form,
        'convenio': convenio,
        'titulo': f'Cargar Documento para: {convenio.numero_convenio}'
    })


@login_required
def documento_descargar(request, pk):
    """Descarga segura de archivo usando FileResponse de Django."""
    doc = get_object_or_404(DocumentoConvenio, pk=pk)
    if not doc.archivo:
        raise Http404("El archivo solicitado no se encuentra disponible.")
    
    file_path = doc.archivo.path
    if not os.path.exists(file_path):
        raise Http404("El archivo físico no fue encontrado en el servidor.")
    
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return response


@login_required
def documento_eliminar(request, pk):
    """Elimina un documento digital del convenio si el usuario está autorizado."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para eliminar documentos.")

    doc = get_object_or_404(DocumentoConvenio, pk=pk)
    inst_id = doc.convenio.institucion.pk
    if request.method == 'POST':
        nombre_doc = doc.nombre
        # Eliminar archivo físico del storage si existe
        if doc.archivo and os.path.exists(doc.archivo.path):
            try:
                os.remove(doc.archivo.path)
            except OSError:
                pass
        doc.delete()
        messages.warning(request, f"Documento '{nombre_doc}' eliminado correctamente.")
        return redirect('institucion_convenio_detalle', pk=inst_id)

    return render(request, 'convenios/confirmar_eliminar_documento.html', {
        'documento': doc
    })


@login_required
def convenio_detalle(request, pk):
    """
    Vista detallada del Convenio SENA con semáforo de vigencia, días restantes,
    beneficios vinculados y expediente documental digital.
    """
    convenio = get_object_or_404(
        ConvenioSENA.objects.select_related('institucion', 'institucion_educativa').prefetch_related('beneficios', 'documentos'),
        pk=pk
    )
    beneficios = convenio.beneficios.all()
    documentos = convenio.documentos.all()
    can_manage = _user_can_manage_convenios(request.user)

    form_beneficio = BeneficioConvenioForm()
    form_doc = DocumentoConvenioForm()

    context = {
        'convenio': convenio,
        'beneficios': beneficios,
        'documentos': documentos,
        'can_manage': can_manage,
        'form_beneficio': form_beneficio,
        'form_doc': form_doc,
    }
    return render(request, 'convenios/convenio_detalle.html', context)


@login_required
def beneficio_crear(request, convenio_id):
    """Registrar un nuevo beneficio articulado al convenio SENA."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para agregar beneficios.")

    convenio = get_object_or_404(ConvenioSENA, pk=convenio_id)
    if request.method == 'POST':
        form = BeneficioConvenioForm(request.POST)
        if form.is_valid():
            ben = form.save(commit=False)
            ben.convenio = convenio
            ben.save()
            messages.success(request, f"Beneficio '{ben.nombre}' vinculado al convenio.")
            return redirect('convenio_detalle', pk=convenio.pk)
        else:
            messages.error(request, "Error al guardar el beneficio. Revise los campos.")
    return redirect('convenio_detalle', pk=convenio.pk)


@login_required
def beneficio_eliminar(request, pk):
    """Eliminar un beneficio del convenio."""
    if not _user_can_manage_convenios(request.user):
        raise PermissionDenied("No tienes permisos para eliminar beneficios.")

    ben = get_object_or_404(BeneficioConvenio, pk=pk)
    conv_id = ben.convenio.pk
    if request.method == 'POST':
        nom = ben.nombre
        ben.delete()
        messages.success(request, f"Beneficio '{nom}' retirado del convenio.")
    return redirect('convenio_detalle', pk=conv_id)

