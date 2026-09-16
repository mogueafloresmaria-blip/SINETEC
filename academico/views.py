import csv
import io
import unicodedata

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.db import transaction
from .models import Ficha, Matricula, ProgramaFormacion
from openpyxl import load_workbook

from .forms import FichaForm, MatriculaRapidaForm, ImportarAprendicesForm
from usuarios.models import PerfilUsuario, Rol


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
    Listado general de Fichas de Media Técnica con filtros y buscador.
    """
    query = request.GET.get('q', '').strip()
    estado_filtro = request.GET.get('estado', '').strip()

    fichas = Ficha.objects.select_related('programa', 'institucion', 'instructor_lider').all()

    if query:
        fichas = fichas.filter(
            Q(codigo_ficha__icontains=query) |
            Q(programa__denominacion__icontains=query) |
            Q(institucion__nombre__icontains=query)
        )

    if estado_filtro:
        fichas = fichas.filter(estado=estado_filtro)

    context = {
        'fichas': fichas,
        'query': query,
        'estado_filtro': estado_filtro,
    }
    return render(request, 'academico/fichas_lista.html', context)


@login_required
def detalle_ficha(request, pk):
    """
    Expediente completo de una ficha técnica: aprendices matriculados,
    competencias curriculares y bitácoras de seguimiento asociadas.
    """
    ficha = get_object_or_404(Ficha.objects.select_related('programa', 'institucion', 'instructor_lider'), pk=pk)
    matriculas = ficha.matriculas.select_related('aprendiz', 'aprendiz__perfil').order_by('aprendiz__last_name')
    seguimientos = ficha.seguimientos.select_related('instructor', 'matricula__aprendiz').order_by('-fecha_visita')[:5]
    competencias = ficha.programa.competencias.prefetch_related('resultados').all()

    context = {
        'ficha': ficha,
        'matriculas': matriculas,
        'seguimientos': seguimientos,
        'competencias': competencias,
    }
    return render(request, 'academico/ficha_detalle.html', context)


@login_required
def crear_ficha(request):
    """
    Apertura de una nueva ficha técnica de Media Técnica.
    """
    if request.method == 'POST':
        form = FichaForm(request.POST)
        if form.is_valid():
            ficha = form.save()
            messages.success(request, f"Ficha {ficha.codigo_ficha} creada exitosamente.")
            return redirect('fichas_detalle', pk=ficha.pk)
        else:
            messages.error(request, "Por favor revise los campos obligatorios.")
    else:
        form = FichaForm()

    return render(request, 'academico/ficha_formulario.html', {'form': form, 'titulo': 'Apertura de Ficha Técnica'})


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

                    messages.success(request, f"Aprendiz {user.get_full_name()} matriculado exitosamente en la Ficha {ficha.codigo_ficha}.")
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
