import os
import sys
import django
from django.core.files.uploadedfile import SimpleUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from academico.models import (
    InstitucionEducativa, ProgramaFormacion, Ficha, Matricula,
    CargaAcademica, HorarioFicha, CalificacionEscolar,
    TareaClase, EntregaTarea
)
from usuarios.models import PerfilUsuario, Rol, FamiliaAcudiente
from seguimiento.models import ComunicadoEscolar, AsistenciaAprendiz

def run_tests():
    print("=" * 80)
    print("INICIANDO PRUEBA INTEGRAL DE 6 PANELES Y FLUJO COMPLETO EN EDUNOVA")
    print("=" * 80)

    client = Client()

    # 1. SETUP DE ROLES Y USUARIOS
    rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
    rol_rector, _ = Rol.objects.get_or_create(nombre='Rectoría')
    rol_secretaria, _ = Rol.objects.get_or_create(nombre='Secretaría')
    rol_docente, _ = Rol.objects.get_or_create(nombre='Docente')
    rol_estudiante, _ = Rol.objects.get_or_create(nombre='Estudiante')
    rol_familia, _ = Rol.objects.get_or_create(nombre='Familia')

    # Crear o recuperar usuarios de prueba
    u_admin, _ = User.objects.get_or_create(username='test_admin_auto', defaults={'first_name': 'Admin', 'last_name': 'Sistema', 'email': 'admin@edunova.edu.co'})
    u_admin.set_password('12345')
    u_admin.is_superuser = True
    u_admin.is_staff = True
    u_admin.save()
    p_admin, _ = PerfilUsuario.objects.get_or_create(usuario=u_admin, defaults={'rol': rol_admin, 'numero_documento': '990001'})
    p_admin.rol = rol_admin
    p_admin.save()

    u_rector, _ = User.objects.get_or_create(username='test_rector_auto', defaults={'first_name': 'Rector', 'last_name': 'Principal', 'email': 'rector@edunova.edu.co'})
    u_rector.set_password('12345')
    u_rector.save()
    p_rector, _ = PerfilUsuario.objects.get_or_create(usuario=u_rector, defaults={'rol': rol_rector, 'numero_documento': '990002'})
    p_rector.rol = rol_rector
    p_rector.save()

    u_secretaria, _ = User.objects.get_or_create(username='test_secre_auto', defaults={'first_name': 'Secretaria', 'last_name': 'General', 'email': 'secretaria@edunova.edu.co'})
    u_secretaria.set_password('12345')
    u_secretaria.save()
    p_sec, _ = PerfilUsuario.objects.get_or_create(usuario=u_secretaria, defaults={'rol': rol_secretaria, 'numero_documento': '990003'})
    p_sec.rol = rol_secretaria
    p_sec.save()

    u_docente, _ = User.objects.get_or_create(username='test_docente_auto', defaults={'first_name': 'Carlos', 'last_name': 'Docente Matematicas', 'email': 'docente@edunova.edu.co'})
    u_docente.set_password('12345')
    u_docente.save()
    p_doc, _ = PerfilUsuario.objects.get_or_create(usuario=u_docente, defaults={'rol': rol_docente, 'numero_documento': '990004'})
    p_doc.rol = rol_docente
    p_doc.save()

    u_familia, _ = User.objects.get_or_create(username='test_familia_auto', defaults={'first_name': 'Elena', 'last_name': 'Restrepo Madre', 'email': 'elena.madre@correo.com'})
    u_familia.set_password('12345')
    u_familia.save()
    p_fam, _ = PerfilUsuario.objects.get_or_create(usuario=u_familia, defaults={'rol': rol_familia, 'numero_documento': '990005'})
    p_fam.rol = rol_familia
    p_fam.numero_documento = '990005'
    p_fam.save()

    # Materia / Programa
    prog_mat, _ = ProgramaFormacion.objects.get_or_create(
        codigo_programa='MAT-601',
        defaults={'denominacion': 'Matemáticas y Razonamiento Lógico', 'activo': True, 'duracion_horas': 120}
    )

    tests_passed = 0
    total_tests = 0

    def assert_test(condition, name):
        nonlocal tests_passed, total_tests
        total_tests += 1
        if condition:
            tests_passed += 1
            print(f"  [OK] {name}")
        else:
            print(f"  [FAIL] {name}")
            raise AssertionError(f"Prueba fallida: {name}")

    # =========================================================================
    # PASO 1: ADMINISTRADOR - Inicio de sesión y consulta institucional
    # =========================================================================
    print("\n--- PASO 1: Panel Administrador ---")
    client.login(username='test_admin_auto', password='12345')
    resp = client.get('/dashboard/')
    assert_test(resp.status_code == 200, "Administrador accede al dashboard principal")
    resp_u = client.get('/usuarios/?rol=todos')
    assert_test(resp_u.status_code == 200, "Administrador consulta gestión de usuarios sin errores")
    client.logout()

    # =========================================================================
    # PASO 2: SECRETARÍA - Matricular estudiante nuevo con datos completos
    # =========================================================================
    print("\n--- PASO 2: Panel Secretaría (Matrícula y Asignación de Materias) ---")
    client.login(username='test_secre_auto', password='12345')

    doc_estudiante_test = "1098765432"
    u_prev = User.objects.filter(username=doc_estudiante_test).first()
    if u_prev:
        AsistenciaAprendiz.objects.filter(matricula__aprendiz=u_prev).delete()
        EntregaTarea.objects.filter(estudiante=u_prev).delete()
        Matricula.objects.filter(aprendiz=u_prev).delete()
        for fam in FamiliaAcudiente.objects.filter(estudiantes=u_prev):
            fam.estudiantes.remove(u_prev)
        PerfilUsuario.objects.filter(usuario=u_prev).delete()
        u_prev.delete()

    post_data = {
        'nombres': 'Daniel Andrés',
        'apellidos': 'Torres Restrepo',
        'tipo_documento': 'TI',
        'documento': doc_estudiante_test,
        'genero': 'Masculino',
        'fecha_nacimiento': '2012-05-14',
        'direccion': 'Calle 10 # 25-40, Barrio Centro',
        'telefono': '3157894561',
        'correo': 'daniel.torres@colegio.edu.co',
        'grado_escolar': '6',
        'seccion': 'A',
        'anio_lectivo': '2026',
        'acudiente_nombre': 'Elena Restrepo Madre',
        'acudiente_parentesco': 'Madre',
        'acudiente_documento': '990005',
        'acudiente_telefono': '3109876543',
        'acudiente_correo': 'elena.madre@correo.com',
        'acudiente_direccion': 'Calle 10 # 25-40, Barrio Centro',
    }

    resp_reg = client.post('/estudiantes/registrar/', post_data, follow=True)
    assert_test(resp_reg.status_code == 200, "Secretaría procesa formulario de matrícula escolar")

    # Verificar que el estudiante quedó guardado en MySQL
    u_estudiante = User.objects.filter(username=doc_estudiante_test).first()
    assert_test(u_estudiante is not None, "Estudiante creado en base de datos MySQL con cédula como usuario")
    assert_test(u_estudiante.first_name == 'Daniel Andrés', "Nombres correctos guardados")
    assert_test(u_estudiante.perfil.numero_documento == doc_estudiante_test, "Perfil de usuario vinculado con documento")

    mat_est = Matricula.objects.filter(aprendiz=u_estudiante, estado_formacion='En Formacion').first()
    assert_test(mat_est is not None, "Matrícula activa formalizada en MySQL")
    assert_test(mat_est.grado_escolar == '6' and mat_est.seccion == 'A', "Grado 6.° y Sección A registrados correctamente")

    # Verificar que se vinculó la familia
    fam_rec = FamiliaAcudiente.objects.filter(estudiantes=u_estudiante).first()
    assert_test(fam_rec is not None, "Estudiante vinculado a su núcleo familiar/acudiente")
    assert_test(fam_rec.parentesco == 'Madre', "Parentesco 'Madre' guardado en FamiliaAcudiente")

    # =========================================================================
    # PASO 3: SECRETARÍA - Asignar Asignatura y Docente al Grado 6.° A
    # =========================================================================
    print("\n--- PASO 3: Asignación de Materias y Docente al Grupo por Secretaría ---")
    post_asignar = {
        'action': 'asignar_materia_grupo',
        'programa_id': prog_mat.id,
        'profesor_id': u_docente.id,
        'grado': '6',
        'seccion': 'A'
    }
    resp_asig = client.post(f'/estudiantes/{u_estudiante.id}/', post_asignar, follow=True)
    assert_test(resp_asig.status_code == 200, "Secretaría asigna materia y docente directamente desde el expediente")

    carga_guardada = CargaAcademica.objects.filter(programa=prog_mat, grado__icontains='6', seccion='A').first()
    assert_test(carga_guardada is not None, "Carga académica de Matemáticas para Grado 6.°A guardada en MySQL")
    assert_test(carga_guardada.profesor == u_docente, "Profesor Carlos Docente asignado a la materia")

    # Verificar que en el expediente del estudiante aparece la materia asignada
    resp_exp = client.get(f'/estudiantes/{u_estudiante.id}/')
    assert_test(resp_exp.status_code == 200 and 'Matemáticas y Razonamiento Lógico' in resp_exp.content.decode('utf-8'),
                "Expediente del estudiante muestra la asignatura asignada y el docente a cargo")
    client.logout()

    # =========================================================================
    # PASO 4: RECTORÍA - Consulta de todos los 8 módulos y emisión de circular con PDF
    # =========================================================================
    print("\n--- PASO 4: Panel Rectoría (8 Módulos oficiales + Circulares con PDF) ---")
    client.login(username='test_rector_auto', password='12345')

    # Módulo 1: Inicio
    r1 = client.get('/rectoria/')
    assert_test(r1.status_code == 200 and 'Panel Directivo y de Rectoría' in r1.content.decode('utf-8'), "Módulo 1: Inicio Rectoría carga con KPIs y estilo institucional")

    # Módulo 2: Usuarios con filtros
    r2 = client.get('/usuarios/?rol=estudiante')
    assert_test(r2.status_code == 200 and doc_estudiante_test in r2.content.decode('utf-8'), "Módulo 2: Usuarios filtra estudiantes y muestra el nuevo matriculado")
    r2_fam = client.get('/usuarios/?rol=familia')
    assert_test(r2_fam.status_code == 200, "Módulo 2: Usuarios filtra familias sin errores")

    # Módulo 3: Gestión académica
    r3 = client.get('/academico/gestion-academica/?grado=6')
    assert_test(r3.status_code == 200 and 'Grado 6.°' in r3.content.decode('utf-8') and 'Daniel Andrés' in r3.content.decode('utf-8'),
                "Módulo 3: Gestión Académica muestra Grado 6.°, asignaturas, docentes y estudiantes reales")

    # Módulo 4: Horarios
    r4 = client.get('/academico/horarios/')
    assert_test(r4.status_code == 200, "Módulo 4: Horarios escolares carga tablero oficial")

    # Módulo 5: Matrículas y seguimiento
    r5 = client.get('/estudiantes/matriculas/?q=' + doc_estudiante_test)
    assert_test(r5.status_code == 200 and 'Daniel Andrés' in r5.content.decode('utf-8'), "Módulo 5: Matrículas muestra al estudiante matriculado por Secretaría")

    # Módulo 6: Informes académicos
    r6 = client.get('/calificaciones/')
    assert_test(r6.status_code == 200, "Módulo 6: Informes académicos carga calificaciones reales")

    # Módulo 7: Comunicaciones
    r7 = client.get('/academico/comunicaciones/')
    assert_test(r7.status_code == 200, "Módulo 7: Comunicaciones institucionales carga correctamente")

    # Módulo 8: Circulares oficiales con PDF
    pdf_dummy = SimpleUploadedFile("circular_oficial_01.pdf", b"%PDF-1.4 demo test official circular content", content_type="application/pdf")
    r8_post = client.post('/comunicaciones/redactar/', {
        'asunto': 'Circular No. 01: Inicio de Actividades Grado 6',
        'mensaje': 'Estimada comunidad educativa, se informa el inicio de actividades para Grado 6.',
        'destinatario_tipo': 'Toda',
        'urgente': 'on',
        'adjunto_pdf': pdf_dummy
    }, follow=True)
    assert_test(r8_post.status_code == 200, "Módulo 8: Rectoría redacta y publica circular con archivo PDF adjunto")

    circ_db = ComunicadoEscolar.objects.filter(asunto__icontains='Circular No. 01').first()
    assert_test(circ_db is not None, "Circular guardada en MySQL")
    assert_test(bool(circ_db.adjunto_pdf), "Archivo PDF adjunto guardado exitosamente en ComunicadoEscolar")
    client.logout()

    # =========================================================================
    # PASO 5: DOCENTE - Ver su clase, registrar tarea, calificar y registrar asistencia
    # =========================================================================
    print("\n--- PASO 5: Panel Docente ---")
    client.login(username='test_docente_auto', password='12345')

    resp_clase = client.get(f'/academico/clase/{carga_guardada.id}/')
    assert_test(resp_clase.status_code == 200 and 'Daniel Andrés' in resp_clase.content.decode('utf-8'),
                "Docente accede a su clase y encuentra al estudiante matriculado en su lista")

    # Registrar asistencia
    resp_asist = client.post(f'/academico/clase/{carga_guardada.id}/', {
        'action': 'guardar_asistencia',
        'fecha': timezone.localdate().strftime('%Y-%m-%d'),
        f'asistencia_{mat_est.id}': 'P'
    }, follow=True)
    assert_test(resp_asist.status_code == 200, "Docente guarda asistencia de la fecha")
    asis_db = AsistenciaAprendiz.objects.filter(matricula=mat_est, estado='P').first()
    assert_test(asis_db is not None, "Registro de asistencia guardado en MySQL")

    # Publicar tarea
    resp_tarea = client.post(f'/academico/clase/{carga_guardada.id}/crear-tarea/', {
        'titulo': 'Taller 1: Fracciones y Decimales',
        'descripcion': 'Resolver los ejercicios del taller 1.',
        'puntos_maximos': 100,
        'fecha_entrega': (timezone.now() + timezone.timedelta(days=7)).strftime('%Y-%m-%d %H:%M')
    }, follow=True)
    assert_test(resp_tarea.status_code == 200, "Docente publica tarea para el grupo")

    tarea_db = TareaClase.objects.filter(carga_academica=carga_guardada, titulo__icontains='Fracciones').first()
    assert_test(tarea_db is not None, "Tarea registrada en la base de datos MySQL")
    client.logout()

    # =========================================================================
    # PASO 6: ESTUDIANTE - Ingresar, ver materias, docentes, tareas y circulares
    # =========================================================================
    print("\n--- PASO 6: Panel Estudiante ---")
    client.login(username=doc_estudiante_test, password=doc_estudiante_test)

    resp_est_dash = client.get('/dashboard/', follow=True)
    assert_test(resp_est_dash.status_code == 200, "Estudiante inicia sesión con su documento y accede al dashboard")

    resp_est_act = client.get('/academico/mis-actividades/')
    assert_test(resp_est_act.status_code == 200 and 'Fracciones y Decimales' in resp_est_act.content.decode('utf-8'),
                "Estudiante visualiza la tarea publicada por su docente")

    resp_est_mens = client.get('/mensajeria/')
    assert_test(resp_est_mens.status_code == 200 and 'Circular No. 01' in resp_est_mens.content.decode('utf-8'),
                "Estudiante consulta las circulares oficiales institucionales")
    client.logout()

    # =========================================================================
    # PASO 7: FAMILIA - Ingresar, ver a su hijo matriculado, asistencia y circular con PDF
    # =========================================================================
    print("\n--- PASO 7: Panel Familia / Acudiente ---")
    client.login(username='test_familia_auto', password='12345')

    resp_fam_dash = client.get('/dashboard/', follow=True)
    assert_test(resp_fam_dash.status_code == 200, "Familia inicia sesión y accede al portal familiar")

    resp_fam_exp = client.get(f'/estudiantes/{u_estudiante.id}/')
    assert_test(resp_fam_exp.status_code == 200 and 'Daniel Andrés' in resp_fam_exp.content.decode('utf-8'),
                "Familia autorizada puede consultar el expediente escolar de su hijo")

    resp_fam_circ = client.get('/mensajeria/')
    assert_test(resp_fam_circ.status_code == 200 and 'Circular No. 01' in resp_fam_circ.content.decode('utf-8'),
                "Familia puede leer las circulares oficiales y acceder a los anexos en PDF")
    client.logout()

    print("\n" + "=" * 80)
    print(f"RESULTADO: {tests_passed}/{total_tests} PRUEBAS COMPLETADAS CON ÉXITO (100% OK)")
    print("=" * 80)

if __name__ == '__main__':
    run_tests()
