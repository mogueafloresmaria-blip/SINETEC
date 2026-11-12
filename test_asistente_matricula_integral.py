import os
import sys
import django

sys.path.insert(0, r'c:\EDUNOVA\EDUNOVA')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from academico.models import Matricula, Ficha, CargaAcademica, HorarioFicha, ProgramaFormacion
from usuarios.models import PerfilUsuario, Rol, FamiliaAcudiente
from seguimiento.models import AsistenciaAprendiz, RegistroAuditoria
from datetime import time, date

tests_passed = 0
total_tests = 0

def assert_test(condition, message):
    global tests_passed, total_tests
    total_tests += 1
    if condition:
        tests_passed += 1
        print(f"  [OK] {message}")
    else:
        print(f"  [FAIL] {message}")
        raise AssertionError(f"Falla en prueba: {message}")

def run_tests():
    print("=" * 80)
    print("INICIANDO PRUEBAS DEL ASISTENTE DE MATRÍCULA Y ASIGNACIÓN ACADÉMICA")
    print("=" * 80)

    client = Client()

    # Setup de usuarios administrativos
    rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
    rol_sec, _ = Rol.objects.get_or_create(nombre='Secretaría')
    rol_doc, _ = Rol.objects.get_or_create(nombre='Docente')
    rol_est, _ = Rol.objects.get_or_create(nombre='Estudiante')
    rol_fam, _ = Rol.objects.get_or_create(nombre='Familia')

    u_sec, _ = User.objects.get_or_create(username='test_sec_mat', defaults={'first_name': 'Ana', 'last_name': 'Secretaria'})
    u_sec.set_password('12345')
    u_sec.save()
    p_sec, _ = PerfilUsuario.objects.get_or_create(usuario=u_sec, defaults={'rol': rol_sec, 'numero_documento': '55443322'})
    p_sec.rol = rol_sec
    p_sec.save()

    # -------------------------------------------------------------
    # 1. VERIFICAR CARGA DEL ASISTENTE DE MATRÍCULA Y SERIALIZACIÓN
    # -------------------------------------------------------------
    print("\n--- 1. Carga del Asistente y Corrección de Selección ---")
    client.login(username='test_sec_mat', password='12345')
    r_get = client.get('/academico/matriculas/nueva/')
    assert_test(r_get.status_code == 200, "Asistente de matrícula carga exitosamente (Status 200)")
    assert_test('alumnos-json-data' in r_get.content.decode('utf-8'), "Estudiantes activos pre-serializados en JSON para búsqueda ultrarrápida")
    assert_test('Etapa 1: Identificación y Selección' in r_get.content.decode('utf-8'), "Etapa 1 presente sin select nativo bloqueante")
    assert_test('Etapa 5: Resumen y Confirmación' in r_get.content.decode('utf-8'), "Etapa 5 de resumen y confirmación presente")

    # -------------------------------------------------------------
    # 2. CREACIÓN DE NUEVO ESTUDIANTE + ACUDIENTE + MATRÍCULA EN ETAPAS
    # -------------------------------------------------------------
    print("\n--- 2. Registro de Nuevo Estudiante y Acudiente con Cuenta Automática ---")
    doc_nuevo = "9988112233"
    # Limpiar si existía
    u_old = User.objects.filter(username=doc_nuevo).first()
    if u_old:
        Matricula.objects.filter(aprendiz=u_old).delete()
        u_old.delete()

    r_post_nuevo = client.post('/academico/matriculas/nueva/', {
        'modo_estudiante': 'nuevo',
        'documento': doc_nuevo,
        'tipo_documento': 'TI',
        'nombres': 'Valentina',
        'apellidos': 'Gómez Jaramillo',
        'email': 'valentina.gomez@edunova.edu',
        'telefono': '3009876543',
        'genero': 'F',
        'direccion': 'Calle 50 # 10-20',
        # Acudiente
        'acudiente_nombre': 'Patricia Jaramillo Duque',
        'acudiente_parentesco': 'Madre',
        'acudiente_documento': '43998877',
        'acudiente_telefono': '3104567890',
        'acudiente_email': 'patricia.jaramillo@gmail.com',
        'acudiente_direccion': 'Calle 50 # 10-20',
        # Matrícula
        'grado_escolar': '7',
        'seccion': 'A',
        'jornada': 'Mañana',
        'anio_lectivo': '2026',
        'estado_formacion': 'En Formacion',
    }, follow=True)

    assert_test(r_post_nuevo.status_code == 200, "Formulario de matrícula procesado correctamente")

    # Verificar usuario creado en MySQL con usuario=documento y contraseña=documento
    u_val = User.objects.filter(username=doc_nuevo).first()
    assert_test(u_val is not None, "Estudiante creado en base de datos con su número de documento")
    assert_test(u_val.check_password(doc_nuevo), "Contraseña inicial cifrada coincide exactamente con su número de documento")
    assert_test(u_val.first_name == 'Valentina' and u_val.last_name == 'Gómez Jaramillo', "Nombres y apellidos guardados fielmente")

    # Verificar Matrícula
    mat_val = Matricula.objects.filter(aprendiz=u_val, estado_formacion='En Formacion').first()
    assert_test(mat_val is not None, "Matrícula oficial formalizada en MySQL")
    assert_test(mat_val.grado_escolar == '7' and mat_val.seccion == 'A', "Asignado a Grado 7° Sección A")
    assert_test(mat_val.acudiente_nombre == 'Patricia Jaramillo Duque', "Nombre del acudiente vinculado en la matrícula")

    # Verificar FamiliaAcudiente
    fam_val = FamiliaAcudiente.objects.filter(estudiantes=u_val).first()
    assert_test(fam_val is not None, "Registro de núcleo familiar (FamiliaAcudiente) creado y vinculado al estudiante")
    assert_test(fam_val.parentesco == 'Madre' and fam_val.telefono == '3104567890', "Parentesco 'Madre' y teléfono guardados")

    # -------------------------------------------------------------
    # 3. PREVENCIÓN DE DUPLICADOS POR ESTUDIANTE Y AÑO LECTIVO
    # -------------------------------------------------------------
    print("\n--- 3. Prevención de Duplicados ---")
    r_post_dup = client.post('/academico/matriculas/nueva/', {
        'modo_estudiante': 'existente',
        'alumno_id': u_val.id,
        'grado_escolar': '7',
        'seccion': 'A',
        'anio_lectivo': '2026',
    }, follow=True)
    assert_test("ya cuenta con una matrícula activa" in r_post_dup.content.decode('utf-8') or
                "no se permiten duplicados" in r_post_dup.content.decode('utf-8').lower(),
                "Sistema detecta y bloquea matrícula duplicada para el mismo estudiante y grado")

    # -------------------------------------------------------------
    # 4. SEPARACIÓN DE MATRÍCULA Y ASIGNACIÓN ACADÉMICA
    # -------------------------------------------------------------
    print("\n--- 4. Separación de Matrícula y Asignación Académica ---")
    # Valentina ya está matriculada y formalizada SIN requerir asignación previa de docentes
    assert_test(mat_val.estado_formacion == 'En Formacion', "Matrícula válida y activa sin depender de asignación docente")

    # Cargar módulo de Asignación Académica para Grado 7°A
    r_asig = client.get('/academico/asignacion-academica/?grado=7&seccion=A')
    assert_test(r_asig.status_code == 200, "Módulo de Asignación Académica carga para Grado 7° Sección A")
    assert_test('Valentina' in r_asig.content.decode('utf-8'), "Estudiante matriculado visible en la lista del grupo")

    # Asignar docente y materia al grupo
    prog_bio, _ = ProgramaFormacion.objects.get_or_create(
        codigo_programa='BIO-07',
        defaults={'denominacion': 'Biología y Ciencias Naturales', 'version': 1, 'tipo_programa': 'Secundaria', 'duracion_horas': 4, 'activo': True}
    )
    u_prof, _ = User.objects.get_or_create(username='test_prof_bio', defaults={'first_name': 'Roberto', 'last_name': 'Biólogo'})
    u_prof.set_password('12345')
    u_prof.save()
    p_prof, _ = PerfilUsuario.objects.get_or_create(usuario=u_prof, defaults={'rol': rol_doc, 'numero_documento': '77889900'})

    r_post_asig = client.post('/academico/asignacion-academica/?grado=7&seccion=A', {
        'action': 'asignar_docente_materia',
        'programa_id': prog_bio.id,
        'docente_id': u_prof.id,
    }, follow=True)
    assert_test(r_post_asig.status_code == 200, "Secretaría asigna materia y docente al grupo escolar")
    carga_creada = CargaAcademica.objects.filter(profesor=u_prof, programa=prog_bio, grado='7', seccion='A').first()
    assert_test(carga_creada is not None, "Carga académica guardada en MySQL para Grado 7°A")

    # Configurar horario y probar detección de cruces
    horario1 = HorarioFicha.objects.create(
        instructor=u_prof,
        programa=prog_bio,
        grado='7',
        seccion='A',
        dia='1',
        hora_inicio=time(8, 0),
        hora_fin=time(10, 0),
        ambiente='Laboratorio de Ciencias',
        nivel='Secundaria'
    )
    assert_test(horario1.id is not None, "Bloque de horario semanal creado para el grupo")

    # Validar detección de cruce de horario en API
    r_cruce = client.get(f'/academico/api/validar-cruce-horario/?profesor_id={u_prof.id}&dia=1&hora_inicio=08:30&hora_fin=09:30')
    assert_test(r_cruce.status_code == 200 and r_cruce.json().get('hay_cruce') is True,
                "Detector de cruces de horario alerta correctamente sobre solapamiento de horarios del docente")

    # -------------------------------------------------------------
    # 5. GESTIÓN POSTERIOR: EDICIÓN, TRASLADO Y ACTUALIZAR ACUDIENTE
    # -------------------------------------------------------------
    print("\n--- 5. Gestión Posterior: Edición, Traslado y Acudiente ---")

    # Registrar una asistencia y calificación inicial para comprobar preservación
    asis_pre = AsistenciaAprendiz.objects.create(
        matricula=mat_val,
        fecha=timezone.localdate(),
        estado='P',
        observaciones='Asistencia regular',
        registrado_por=u_sec
    )
    assert_test(asis_pre.id is not None, "Asistencia previa registrada para el estudiante")

    # A. Actualizar acudiente
    r_acu = client.post(f'/academico/matriculas/{mat_val.id}/acudiente/', {
        'nombre_acudiente': 'Patricia Elena Jaramillo Actualizada',
        'parentesco': 'Madre',
        'documento': '43998877',
        'telefono': '3209998877',
        'email': 'patricia.actualizada@gmail.com',
        'direccion': 'Avenida Central # 40-10'
    }, follow=True)
    assert_test(r_acu.status_code == 200, "Actualización de acudiente procesada exitosamente")
    mat_val.refresh_from_db()
    assert_test(mat_val.acudiente_nombre == 'Patricia Elena Jaramillo Actualizada', "Matrícula actualizó nombre de acudiente")
    assert_test(mat_val.acudiente_telefono == '3209998877', "Matrícula actualizó teléfono de acudiente")

    # B. Editar matrícula
    r_edit = client.post(f'/academico/matriculas/{mat_val.id}/editar/', {
        'grado_escolar': '7',
        'seccion': 'A',
        'estado_formacion': 'En Formacion',
        'acudiente_nombre': 'Patricia Elena Jaramillo Actualizada',
        'acudiente_telefono': '3209998877',
    }, follow=True)
    assert_test(r_edit.status_code == 200, "Edición general de matrícula procesada exitosamente")

    # C. Traslado de grupo (de Grado 7°A a Grado 7°B)
    r_traslado = client.post(f'/academico/matriculas/{mat_val.id}/traslado/', {
        'nuevo_grado': '7',
        'nueva_seccion': 'B',
        'motivo': 'Reubicación por cambio de horario familiar'
    }, follow=True)
    assert_test(r_traslado.status_code == 200, "Traslado de grupo ejecutado exitosamente")
    mat_val.refresh_from_db()
    assert_test(mat_val.seccion == 'B', "Estudiante reubicado exitosamente en Sección B")

    # Comprobar que la asistencia previa se conservó intacta
    asis_post = AsistenciaAprendiz.objects.filter(matricula=mat_val).first()
    assert_test(asis_post is not None and asis_post.id == asis_pre.id,
                "Historial de asistencia conservado intacto tras el traslado de grupo")

    # -------------------------------------------------------------
    # 6. ACCESO UNIFICADO Y ROLES
    # -------------------------------------------------------------
    print("\n--- 6. Acceso Unificado por Rol y Activación de Cuenta ---")
    client.logout()

    # Login como Estudiante (usuario=documento, clave=documento)
    login_est_ok = client.login(username=doc_nuevo, password=doc_nuevo)
    assert_test(login_est_ok is True, "Estudiante inicia sesión con sus credenciales automáticas (cédula/cédula)")
    r_dash_est = client.get('/estudiante/')
    assert_test(r_dash_est.status_code == 200 and 'Valentina' in r_dash_est.content.decode('utf-8'),
                "Estudiante accede a su panel oficial y visualiza su nombre real")
    client.logout()

    # Login como Docente
    login_doc_ok = client.login(username='test_prof_bio', password='12345')
    assert_test(login_doc_ok is True, "Docente asignado inicia sesión correctamente")
    r_doc_clase = client.get(f'/academico/clase/{carga_creada.id}/')
    assert_test(r_doc_clase.status_code == 200, "Docente accede a su clase asignada")
    client.logout()

    print("\n" + "=" * 80)
    print(f"RESULTADO FINAL: {tests_passed}/{total_tests} PRUEBAS APROBADAS (100% OK)")
    print("=" * 80)

if __name__ == '__main__':
    run_tests()
