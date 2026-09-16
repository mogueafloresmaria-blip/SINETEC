from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import InstitucionEducativa
from .forms import InstitucionEducativaForm


@login_required
def lista_instituciones(request):
    """
    Directorio interactivo de Instituciones Educativas con buscador reactivo.
    """
    query = request.GET.get('q', '').strip()
    municipio_filtro = request.GET.get('municipio', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    instituciones = InstitucionEducativa.objects.all()

    if query:
        instituciones = instituciones.filter(
            Q(nombre__icontains=query) |
            Q(codigo_dane__icontains=query) |
            Q(rector_nombre__icontains=query)
        )

    if municipio_filtro:
        instituciones = instituciones.filter(municipio__iexact=municipio_filtro)

    if estado_filtro == 'activas':
        instituciones = instituciones.filter(activa=True)

    # Lista de municipios únicos para el filtro
    municipios = InstitucionEducativa.objects.values_list('municipio', flat=True).distinct().order_by('municipio')

    context = {
        'instituciones': instituciones,
        'query': query,
        'municipio_filtro': municipio_filtro,
        'estado_filtro': estado_filtro,
        'municipios': municipios,
    }
    return render(request, 'instituciones/lista.html', context)


@login_required
def detalle_institucion(request, pk):
    """
    Ficha de detalle de un colegio articulado y sus fichas técnicas vigentes.
    """
    institucion = get_object_or_404(InstitucionEducativa, pk=pk)
    fichas = institucion.fichas.select_related('programa', 'instructor_lider').order_by('-fecha_inicio')
    return render(request, 'instituciones/detalle.html', {'institucion': institucion, 'fichas': fichas})


@login_required
def crear_institucion(request):
    """
    Registro de una nueva institución educativa en convenio.
    """
    if request.method == 'POST':
        form = InstitucionEducativaForm(request.POST)
        if form.is_valid():
            colegio = form.save()
            messages.success(request, f"Colegio '{colegio.nombre}' registrado exitosamente.")
            return redirect('instituciones_detalle', pk=colegio.pk)
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = InstitucionEducativaForm()

    return render(request, 'instituciones/formulario.html', {'form': form, 'titulo': 'Registrar Institución Educativa'})


@login_required
def editar_institucion(request, pk):
    """
    Edición de datos de una institución educativa existente.
    """
    institucion = get_object_or_404(InstitucionEducativa, pk=pk)
    if request.method == 'POST':
        form = InstitucionEducativaForm(request.POST, instance=institucion)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos del colegio '{institucion.nombre}' actualizados correctamente.")
            return redirect('instituciones_detalle', pk=institucion.pk)
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
    else:
        form = InstitucionEducativaForm(instance=institucion)

    return render(request, 'instituciones/formulario.html', {'form': form, 'titulo': 'Editar Institución Educativa', 'institucion': institucion})
