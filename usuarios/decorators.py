import unicodedata
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q


def _normalizar_texto(texto):
    if not texto:
        return ''
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower().strip()


def obtener_url_redireccion_por_rol(user):
    """
    Determina la URL de destino según el rol institucional real del usuario en MySQL.
    """
    if not user or not user.is_authenticated:
        return 'login'
    if user.is_superuser:
        return 'dashboard'

    perfil = getattr(user, 'perfil', None)
    if not perfil or not perfil.rol:
        return 'dashboard'

    rol_nombre = _normalizar_texto(perfil.rol.nombre)

    cats = _obtener_categorias_rol(rol_nombre)

    if 'ESTUDIANTE' in cats:
        return 'aprendiz_dashboard'
    elif 'FAMILIA' in cats:
        return 'familia_portal'
    elif 'DOCENTE' in cats:
        return 'instructor_dashboard'
    elif 'SECRETARIA' in cats:
        return 'secretaria_dashboard'
    elif 'DIRECTIVO' in cats:
        return 'rectoria_dashboard'
    else:
        return 'dashboard'


def _obtener_categorias_rol(texto):
    """
    Retorna el conjunto de categorías institucionales a las que pertenece un rol o texto:
    - 'ADMIN': Administrador, Superusuario
    - 'DIRECTIVO': Rector, Rectoría, Coordinador, Directivo
    - 'SECRETARIA': Secretaría, Secretaria, Auxiliar
    - 'DOCENTE': Docente, Profesor, Instructor, Maestro, Tutor
    - 'ESTUDIANTE': Estudiante, Aprendiz, Alumno
    - 'FAMILIA': Familia, Acudiente, Padre, Madre, Tutor Legal
    """
    t = _normalizar_texto(texto)
    cats = set()
    if not t:
        return cats

    if any(k in t for k in ['admin', 'super']):
        cats.add('ADMIN')
    if any(k in t for k in ['rector', 'coordinad', 'directiv']):
        cats.add('DIRECTIVO')
    if any(k in t for k in ['secretar']):
        cats.add('SECRETARIA')
    if any(k in t for k in ['docent', 'profesor', 'instructor', 'maestr']):
        cats.add('DOCENTE')
    if any(k in t for k in ['estudiant', 'aprendiz', 'alumno']):
        cats.add('ESTUDIANTE')
    if any(k in t for k in ['famili', 'acudient', 'padre', 'madre']):
        cats.add('FAMILIA')

    return cats


def bloquear_estudiantes(view_func):
    """Impide el acceso del rol Estudiante a vistas que no son módulos estudiantiles."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            perfil = getattr(request.user, 'perfil', None)
            rol_nombre = perfil.rol.nombre if perfil and perfil.rol else ''
            if 'ESTUDIANTE' in _obtener_categorias_rol(rol_nombre):
                messages.error(request, 'Esta función no está disponible para el rol Estudiante.')
                return redirect(obtener_url_redireccion_por_rol(request.user))
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def requerir_roles(*roles_permitidos):
    """
    Decorador de seguridad institucional que verifica en Backend si el usuario autenticado
    tiene un Rol formal compatible con 'roles_permitidos'.
    Reconoce sinónimos escolares (Profesor / Docente, Docente I.E., Instructor, etc.).
    """
    categorias_permitidas = set()
    roles_norm_set = set()
    for r in roles_permitidos:
        r_norm = _normalizar_texto(r)
        roles_norm_set.add(r_norm)
        categorias_permitidas.update(_obtener_categorias_rol(r))

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # Superusuarios de Django tienen acceso maestro total
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            perfil = getattr(request.user, 'perfil', None)
            if not perfil or not perfil.rol:
                if 'ADMIN' in categorias_permitidas:
                    return view_func(request, *args, **kwargs)

            if perfil and perfil.rol:
                rol_nombre = perfil.rol.nombre
                user_norm = _normalizar_texto(rol_nombre)
                user_cats = _obtener_categorias_rol(rol_nombre)

                # Administradores institucionales tienen acceso a vistas de gestión
                if 'ADMIN' in user_cats:
                    return view_func(request, *args, **kwargs)

                # Coincidencia por categoría institucional (e.g. DOCENTE, DIRECTIVO, SECRETARIA, etc.)
                if bool(user_cats & categorias_permitidas):
                    return view_func(request, *args, **kwargs)

                # Directivos (Rector / Coordinador) tienen acceso a vistas de gestión académica y reportes
                if 'DIRECTIVO' in user_cats and bool(categorias_permitidas & {'DOCENTE', 'SECRETARIA', 'ADMIN'}):
                    return view_func(request, *args, **kwargs)

                # Coincidencia por subcadena o coincidencia de prefijo
                for r in roles_norm_set:
                    if r in user_norm or user_norm in r or (len(r) >= 4 and user_norm.startswith(r[:4])):
                        return view_func(request, *args, **kwargs)

            # Si el usuario no está autorizado para esta vista según su rol:
            messages.error(
                request,
                "Acceso Restringido (Seguridad SINETEC): Tu rol de usuario no tiene permisos para acceder a esta sección."
            )
            return redirect(obtener_url_redireccion_por_rol(request.user))
        return _wrapped_view
    return decorator


def solo_admin(view_func):
    return requerir_roles('Administrador')(view_func)


def solo_rectoria_o_admin(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador')(view_func)


def solo_coordinador_o_admin(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador')(view_func)


def solo_secretaria_o_coordinador(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Secretaría', 'Secretaria')(view_func)


def solo_secretaria(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Secretaría', 'Secretaria')(view_func)


def solo_instructor(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Docente', 'Docente I.E.', 'Instructor', 'Instructor SENA', 'Profesor / Docente')(view_func)


def solo_docente(view_func):
    return requerir_roles('Administrador', 'Rectoría', 'Rector', 'Coordinador', 'Docente', 'Docente I.E.', 'Instructor', 'Instructor SENA', 'Profesor / Docente')(view_func)


def solo_aprendiz(view_func):
    return requerir_roles('Estudiante', 'Aprendiz', 'Alumno')(view_func)


def solo_familia(view_func):
    return requerir_roles('Familia/Acudiente', 'Familia', 'Acudiente', 'Familia / Acudiente')(view_func)


def validar_propietario_o_coordinador(request, estudiante_user):
    """
    Regla de seguridad anti-IDOR estricta:
    - Superusuarios, Administradores, Rectoría y Secretaría tienen acceso institucional.
    - Docentes pueden acceder a los estudiantes de sus cursos/fichas.
    - Estudiantes solo pueden consultar su propio expediente.
    - Familias/Acudientes solo pueden consultar los estudiantes asignados a su núcleo familiar.
    Cualquier intento no autorizado lanza PermissionDenied (HTTP 403).
    """
    if request.user.is_superuser:
        return True

    perfil = getattr(request.user, 'perfil', None)
    rol_nombre = _normalizar_texto(perfil.rol.nombre) if (perfil and perfil.rol) else ''

    # 1. Autoridad institucional
    if any(r in rol_nombre for r in ['admin', 'rector', 'coordinad', 'secretar']):
        return True

    # 2. Docentes (verificar si el estudiante pertenece a un grupo/grado/sección con CargaAcademica activa)
    if any(r in rol_nombre for r in ['docente', 'instructor', 'profesor']):
        from academico.models import Matricula, CargaAcademica
        cargas_docente = CargaAcademica.objects.filter(profesor=request.user)
        if not cargas_docente.exists():
            raise PermissionDenied("Violación de Seguridad: Como docente, no tienes asignaciones académicas vigentes.")

        docente_grados_secciones = set()
        docente_grados = set()
        for c in cargas_docente:
            g_clean = ''.join(ch for ch in str(c.grado or '') if ch.isdigit())
            sec_clean = str(c.seccion or '').strip().upper()
            if g_clean:
                docente_grados.add(g_clean)
                if sec_clean:
                    docente_grados_secciones.add((g_clean, sec_clean))

        matriculas_est = Matricula.objects.filter(aprendiz=estudiante_user)
        es_estudiante_propio = False
        for m in matriculas_est:
            m_g = ''.join(ch for ch in str(m.grado_escolar or '') if ch.isdigit())
            m_sec = str(m.seccion or '').strip().upper()
            if (m_g, m_sec) in docente_grados_secciones:
                es_estudiante_propio = True
                break
            if m_g in docente_grados and not m_sec:
                es_estudiante_propio = True
                break
            if m_g in docente_grados:
                es_estudiante_propio = True
                break

        if es_estudiante_propio:
            return True
        raise PermissionDenied("Violación de Seguridad: Como docente, este estudiante no pertenece a ninguno de tus cursos asignados.")

    # 3. Familias y Acudientes (verificar asociación con el estudiante)
    if any(r in rol_nombre for r in ['famili', 'acudiente']) or (hasattr(request, 'session') and (request.session.get('estudiante_fam_doc') or request.session.get('familia_id'))):
        from usuarios.models import FamiliaAcudiente
        doc_acudiente = perfil.numero_documento if perfil else ''
        identificadores = Q()
        tiene_identificador = False
        if doc_acudiente:
            identificadores |= Q(documento=doc_acudiente)
            tiene_identificador = True
        if hasattr(request, 'user') and getattr(request.user, 'email', None):
            identificadores |= Q(email__iexact=request.user.email)
            tiene_identificador = True
        if hasattr(request, 'session') and request.session.get('familia_id'):
            identificadores |= Q(id=request.session.get('familia_id'))
            tiene_identificador = True

        # Validación por registro de FamiliaAcudiente
        if tiene_identificador and FamiliaAcudiente.objects.filter(identificadores, estudiantes=estudiante_user).exists():
            return True

        # Validación por sesión activa del estudiante consultado
        if hasattr(request, 'session') and request.session.get('estudiante_fam_doc'):
            doc_sesion = str(request.session.get('estudiante_fam_doc')).strip()
            est_doc = str(getattr(getattr(estudiante_user, 'perfil', None), 'numero_documento', '')).strip()
            if doc_sesion and (doc_sesion == est_doc or doc_sesion == estudiante_user.username):
                return True

        raise PermissionDenied("Violación de Seguridad: No tienes autorización para consultar la información privada de este estudiante.")

    # 4. Estudiantes (únicamente su propio expediente)
    if any(r in rol_nombre for r in ['estudiante', 'aprendiz', 'alumno']):
        if request.user.id == estudiante_user.id:
            return True
        raise PermissionDenied("Violación de Seguridad: Como estudiante, solo tienes autorización para consultar tu propio expediente.")

    raise PermissionDenied("Violación de Seguridad SINETEC: No estás autorizado para acceder a este expediente estudiantil.")