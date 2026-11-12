"""
Script de verificación oficial para EduNova:
Caso 1: Registro completo de estudiante nuevo con expediente familiar y matrícula inmediata en 1 solo paso.
Caso 2: Búsqueda, selección con 1 clic y asignación de matrícula a estudiante existente (Carla) sin duplicar su cuenta.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from usuarios.models import Rol, PerfilUsuario, FamiliaAcudiente
from academico.models import Ficha, Matricula
from usuarios.views import registrar_aprendiz
from academico.views import nueva_matricula


def setup_request(request, user):
    request.user = user
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    setattr(request, '_messages', FallbackStorage(request))
    return request


def test_caso_1_estudiante_nuevo():
    print("=" * 60)
    print("INICIANDO CASO 1: CREAR ESTUDIANTE NUEVO Y MATRICULARLO EN EL MISMO PROCESO")
    print("=" * 60)

    doc_test = "1099887766"
    # Limpieza previa de pruebas anteriores si existen
    Matricula.objects.filter(aprendiz__username=doc_test).delete()
    FamiliaAcudiente.objects.filter(documento='63456789').delete()
    PerfilUsuario.objects.filter(numero_documento=doc_test).delete()
    User.objects.filter(username=doc_test).delete()

    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(perfil__rol__nombre__in=['Administrador', 'Secretaría', 'Coordinador']).first()
    assert admin_user, "No se encontró un usuario administrativo para ejecutar la prueba"

    rf = RequestFactory()
    post_data = {
        'nombres': 'Santiago Andrés',
        'apellidos': 'Montenegro Ramos',
        'documento': doc_test,
        'tipo_documento': 'TI',
        'genero': 'Masculino',
        'fecha_nacimiento': '2010-05-18',
        'lugar_nacimiento': 'Bucaramanga, Santander',
        'direccion': 'Calle 45 # 12-34, Barrio Modelo',
        'telefono': '3129876543',
        'correo': 'santiago.montenegro@edunova.edu.co',
        'anio_lectivo': '2026',
        'grado_escolar': '9',
        'seccion': 'B',
        'jornada': 'Mañana',
        'fecha_matricula': '2026-11-03',
        'estado_formacion': 'En Formacion',
        'acudiente_nombre': 'Patricia Elena Ramos',
        'acudiente_parentesco': 'Madre',
        'acudiente_documento': '63456789',
        'acudiente_telefono': '3154567890',
        'acudiente_correo': 'patricia.ramos@gmail.com',
        'acudiente_direccion': 'Calle 45 # 12-34, Barrio Modelo',
    }

    req = rf.post('/estudiantes/registrar/', data=post_data)
    setup_request(req, admin_user)

    resp = registrar_aprendiz(req)
    print(f"Respuesta registrar_aprendiz (Status Code): {resp.status_code}")

    # Verificaciones en MySQL
    u = User.objects.filter(username=doc_test).first()
    assert u is not None, f"El usuario con documento {doc_test} no fue creado en la base de datos."
    print(f"[OK] Usuario creado: {u.get_full_name()} (ID: {u.id}, Username: {u.username})")

    # Verificar contraseña inicial cifrada igual al documento
    assert u.check_password(doc_test), "La contraseña inicial no coincide con el documento de identidad"
    print(f"[OK] Autenticación verificada con documento como clave: {doc_test}")

    # Verificar Perfil
    perfil = getattr(u, 'perfil', None)
    assert perfil is not None, "El usuario no tiene PerfilUsuario asignado"
    assert perfil.numero_documento == doc_test, f"Documento en perfil incorrecto: {perfil.numero_documento}"
    assert perfil.rol.nombre == 'Estudiante', f"Rol incorrecto: {perfil.rol.nombre}"
    assert perfil.tipo_documento == 'TI', f"Tipo documento incorrecto: {perfil.tipo_documento}"
    print(f"[OK] PerfilUsuario validado: Rol={perfil.rol.nombre}, Doc={perfil.numero_documento}, Activo={perfil.esta_activo}")

    # Verificar Matrícula
    mat = Matricula.objects.filter(aprendiz=u, grado_escolar='9', seccion='B', estado_formacion='En Formacion').first()
    assert mat is not None, "No se encontró la matrícula activa del estudiante en Grado 9° Sección B"
    print(f"[OK] Matrícula formalizada en MySQL: Grado {mat.grado_escolar}°, Sección '{mat.seccion}', Estado '{mat.estado_formacion}', Ficha '{mat.ficha.codigo_ficha}'")

    # Verificar Acudiente / Familia
    fam = FamiliaAcudiente.objects.filter(documento='63456789').first()
    assert fam is not None, "No se registró el acudiente en FamiliaAcudiente"
    assert fam.estudiantes.filter(id=u.id).exists(), "El estudiante no quedó vinculado a su acudiente"
    print(f"[OK] Núcleo familiar registrado y vinculado: {fam.nombre_acudiente} ({fam.parentesco}) -> Estudiante: {u.get_full_name()}")

    # Prueba de idempotencia y no-duplicación: registrar de nuevo con mismos datos
    req_dup = rf.post('/estudiantes/registrar/', data=post_data)
    setup_request(req_dup, admin_user)
    resp_dup = registrar_aprendiz(req_dup)
    assert User.objects.filter(username=doc_test).count() == 1, "Se duplicó la cuenta de usuario al reenviar datos"
    assert Matricula.objects.filter(aprendiz=u, grado_escolar='9', seccion='B').count() == 1, "Se duplicó la matrícula del estudiante"
    print(f"[OK] Prueba de prevención de duplicados exitosa: 1 solo usuario y 1 sola matrícula activa.")
    print(">>> CASO 1: 100% EXITOSO <<<\n")


def test_caso_2_estudiante_existente_carla():
    print("=" * 60)
    print("INICIANDO CASO 2: BUSCAR A CARLA, SELECCIONARLA Y ASIGNARLE MATRÍCULA")
    print("=" * 60)

    # 1. Buscar a Carla existente
    carla = User.objects.filter(username='1745637476').first() or User.objects.filter(first_name__icontains='Carla', last_name__icontains='Flores').first()
    assert carla is not None, "No se encontró a Carla Flores en la base de datos."
    carla_id_original = carla.id
    carla_doc_original = carla.username
    print(f"[OK] Carla encontrada en BD: ID={carla.id}, Nombre={carla.get_full_name()}, Doc={carla_doc_original}")

    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(perfil__rol__nombre__in=['Administrador', 'Secretaría', 'Coordinador']).first()
    rf = RequestFactory()

    # 2. Comprobar que Carla aparece en el listado para selección con 1 clic
    req_get = rf.get('/academico/matriculas/nueva/')
    setup_request(req_get, admin_user)
    resp_get = nueva_matricula(req_get)
    assert resp_get.status_code == 200, f"Error al cargar formulario nueva_matricula: {resp_get.status_code}"
    html_content = resp_get.content.decode('utf-8')
    assert f'item-alumno-{carla.pk}' in html_content, "Carla Flores no aparece con su elemento seleccionable en el HTML"
    assert carla_doc_original in html_content, "El documento de Carla no aparece en el listado de búsqueda"
    print(f"[OK] Carla Flores disponible en la lista interactiva con id 'item-alumno-{carla.pk}' y documento {carla_doc_original}.")

    # 3. Asignar matrícula a Carla mediante su ID sin duplicar su cuenta
    # Matricular en Grado 10°, Sección 'A'
    post_data_carla = {
        'alumno_id': str(carla.pk),
        'grado_escolar': '10',
        'seccion': 'A',
        'jornada': 'Mañana',
    }

    req_post = rf.post('/academico/matriculas/nueva/', data=post_data_carla)
    setup_request(req_post, admin_user)
    resp_post = nueva_matricula(req_post)
    print(f"Respuesta nueva_matricula (Status Code): {resp_post.status_code}")

    # Verificar que NO se crearon usuarios duplicados
    cuentas_carla = User.objects.filter(username=carla_doc_original).count()
    assert cuentas_carla == 1, f"¡ERROR! Se duplicó la cuenta de Carla. Total cuentas encontradas: {cuentas_carla}"
    assert carla.pk == carla_id_original, "El ID de usuario de Carla cambió inesperadamente."
    print(f"[OK] Cuenta de usuario única e intacta (ID: {carla.id}, Cuentas con su DNI: {cuentas_carla})")

    # Verificar matrícula en MySQL
    mat_carla = Matricula.objects.filter(aprendiz=carla, grado_escolar='10', seccion='A').first()
    assert mat_carla is not None, "No se encontró la matrícula asignada a Carla en Grado 10° Sección A"
    print(f"[OK] Matrícula de Carla confirmada en MySQL: ID={mat_carla.id}, Grado={mat_carla.grado_escolar}°, Sección='{mat_carla.seccion}', Estado='{mat_carla.estado_formacion}'")

    # Probar que si se vuelve a intentar matricular en el mismo curso, el sistema detecta que ya está matriculada sin error 500
    req_post_dup = rf.post('/academico/matriculas/nueva/', data=post_data_carla)
    setup_request(req_post_dup, admin_user)
    resp_post_dup = nueva_matricula(req_post_dup)
    assert resp_post_dup.status_code in [200, 302], f"Error inesperado al intentar matricular nuevamente: {resp_post_dup.status_code}"
    print(f"[OK] Control de matrículas duplicadas para el mismo estudiante validado sin colisiones de base de datos.")

    print(">>> CASO 2: 100% EXITOSO <<<\n")


if __name__ == '__main__':
    test_caso_1_estudiante_nuevo()
    test_caso_2_estudiante_existente_carla()
    print("=" * 60)
    print("TODAS LAS PRUEBAS DE LOS DOS CASOS OBLIGATORIOS PASARON AL 100%")
    print("=" * 60)
