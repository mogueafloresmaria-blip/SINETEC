import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()
from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.contrib.auth.models import User
from academico.models import Matricula, CargaAcademica, ProgramaFormacion, TareaClase
from seguimiento.models import Notificacion, AsistenciaAprendiz

def run_tests():
    print("=" * 70)
    print("EJECUTANDO SUITE COMPLETA DE AUDITORÍA Y VERIFICACIÓN EDUNOVA")
    print("=" * 70)

    # 1. VERIFICACIÓN DE ESTADO DEMOSTRACIÓN EN BASE DE DATOS
    print("\n[1] Verificando estado estricto de la base de datos (Demostración)...")
    docentes_activos = User.objects.filter(is_active=True, perfil__rol__nombre__icontains='Docente')
    estudiantes_activos = User.objects.filter(is_active=True, perfil__rol__nombre='Estudiante')
    matriculas_activas = Matricula.objects.filter(estado_formacion='En Formacion', aprendiz__is_active=True)

    print(f" -> Docentes activos encontrados: {docentes_activos.count()} (Esperado: 1)")
    assert docentes_activos.count() == 1, f"Error: Se esperaban 1 docente activo, pero hay {docentes_activos.count()}"
    docente = docentes_activos.first()
    print(f"    Docente: {docente.username} - {docente.get_full_name()}")

    print(f" -> Estudiantes activos encontrados: {estudiantes_activos.count()} (Esperado: 1)")
    assert estudiantes_activos.count() == 1, f"Error: Se esperaba 1 estudiante activo, pero hay {estudiantes_activos.count()}"
    est = estudiantes_activos.first()
    print(f"    Estudiante: {est.username} - {est.get_full_name()}")
    assert est.username == 'est1' and 'Juan' in est.get_full_name(), "El estudiante activo debe ser Juan Pérez"

    print(f" -> Matrículas activas encontradas: {matriculas_activas.count()} (Esperado: 1)")
    assert matriculas_activas.count() == 1, f"Error: Se esperaba 1 matrícula activa, pero hay {matriculas_activas.count()}"
    mat = matriculas_activas.first()
    print(f"    Matrícula: {mat.aprendiz.get_full_name()} · Grado {mat.grado_escolar}°{mat.seccion}")
    assert '10' in str(mat.grado_escolar), "Juan Pérez debe estar matriculado en Grado 10"

    # Verificar acudiente
    acudiente_user = User.objects.filter(username='familia', is_active=True).first()
    assert acudiente_user is not None, "El usuario acudiente 'familia' debe existir y estar activo"
    print(f"    Acudiente: {acudiente_user.username} - {acudiente_user.get_full_name()}")

    # Verificar ausencia de tareas y notificaciones ficticias
    notifs_est1 = Notificacion.objects.filter(usuario=est).count()
    tareas_count = TareaClase.objects.count()
    asists_count = AsistenciaAprendiz.objects.count()
    print(f" -> Notificaciones Juan Pérez: {notifs_est1} (Esperado: 0)")
    print(f" -> Tareas globales: {tareas_count} (Esperado: 0)")
    print(f" -> Asistencias registradas: {asists_count} (Esperado: 0)")
    assert notifs_est1 == 0, "Juan Pérez no debe tener notificaciones ficticias"
    assert tareas_count == 0, "No deben existir tareas ficticias de demostración"
    assert asists_count == 0, "No deben existir asistencias ficticias de prueba"
    print(" [OK] Estado de la Base de Datos verificado exitosamente.")

    # 2. PRUEBA DE ACCESO A LOS SEIS PANELES
    print("\n[2] Probando acceso HTTP a los 6 paneles institucionales...")
    c = Client()

    # Panel 1: Administrador
    admin_user = User.objects.get(username='admin')
    c.force_login(admin_user)
    r_admin = c.get('/dashboard/')
    print(f" -> Panel Administrador (/dashboard/): Status {r_admin.status_code}")
    assert r_admin.status_code == 200
    assert r_admin.context['total_docentes'] == 1, f"Admin debe mostrar 1 docente activo, mostró {r_admin.context['total_docentes']}"
    assert r_admin.context['total_aprendices'] == 1, f"Admin debe mostrar 1 estudiante activo, mostró {r_admin.context['total_aprendices']}"
    assert r_admin.context['matriculas_anio'] == 1, f"Admin debe mostrar 1 matrícula activa, mostró {r_admin.context['matriculas_anio']}"
    print("    [OK] Panel Administrador: Métricas reales confirmadas (1 docente, 1 estudiante, 1 matrícula).")

    # Panel 2: Rectoría
    rector_user = User.objects.get(username='rector')
    c.force_login(rector_user)
    r_rector = c.get('/rectoria/')
    print(f" -> Panel Rectoría (/rectoria/): Status {r_rector.status_code}")
    assert r_rector.status_code == 200
    print("    [OK] Panel Rectoría accesible y operativo.")

    # Panel 3: Secretaría
    sec_user = User.objects.get(username='secretaria')
    c.force_login(sec_user)
    r_sec = c.get('/secretaria/')
    print(f" -> Panel Secretaría (/secretaria/): Status {r_sec.status_code}")
    assert r_sec.status_code == 200
    print("    [OK] Panel Secretaría accesible y operativo.")

    # Panel 4: Docente
    c.force_login(docente)
    r_doc = c.get('/docente/')
    print(f" -> Panel Docente (/docente/): Status {r_doc.status_code}")
    assert r_doc.status_code == 200
    # Comprobar estudiantes del docente
    total_est_doc = r_doc.context.get('total_estudiantes_docente', 0)
    print(f"    Estudiantes asociados al docente: {total_est_doc} (Esperado: 1)")
    assert total_est_doc == 1, f"El docente solo debe tener 1 estudiante activo (Juan Pérez), pero reportó {total_est_doc}"
    todos_est = r_doc.context.get('todos_mis_estudiantes', [])
    assert len(todos_est) == 1 and todos_est[0].aprendiz.username == 'est1', "Solo debe figurar Juan Pérez"
    # Verificar contador por asignatura
    for asig in r_doc.context.get('asignaturas_metricas', []):
        print(f"    Materia '{asig['nombre']}': {asig['total_estudiantes']} estudiantes (Esperado: <= 1)")
        assert asig['total_estudiantes'] <= 1, f"La asignatura {asig['nombre']} mostró {asig['total_estudiantes']} estudiantes (no puede ser 4)"
    print("    [OK] Panel Docente: Muestra únicamente a Juan Pérez con contadores exactos.")

    # Panel 5: Familia
    c.force_login(acudiente_user)
    r_fam = c.get('/familia/')
    print(f" -> Panel Familia (/familia/): Status {r_fam.status_code}")
    assert r_fam.status_code == 200
    print("    [OK] Panel Familia accesible y operativo.")

    # Panel 6: Estudiante (Juan Pérez)
    c.force_login(est)
    r_est = c.get('/estudiante/')
    print(f" -> Panel Estudiante (/estudiante/): Status {r_est.status_code}")
    assert r_est.status_code == 200
    # Verificar subpaneles
    for sub in ['calificaciones', 'horario', 'asignaturas', 'actividades', 'notificaciones']:
        r_sub = c.get(f'/estudiante/{sub}/')
        assert r_sub.status_code == 200, f"Error accediendo a subpanel {sub} de estudiante"
    print("    [OK] Panel Estudiante y todos sus subpaneles accesibles e interactivos.")

    # 3. PRUEBA DE CARGA ACADÉMICA (DISEÑO Y FUNCIONALIDAD COMPLETA)
    print("\n[3] Probando módulo de Carga Académica (Admin)...")
    c.force_login(admin_user)
    r_carga = c.get('/academico/programas/')
    print(f" -> Carga Académica GET (/academico/programas/): Status {r_carga.status_code}")
    assert r_carga.status_code == 200
    assert 'cardFormularioCarga' in r_carga.content.decode('utf-8')
    assert 'Editar Asignación' in r_carga.content.decode('utf-8') or 'editarCarga' in r_carga.content.decode('utf-8')

    # Crear una nueva asignación de prueba
    prog = ProgramaFormacion.objects.filter(activo=True).first()
    post_data_crear = {
        'profesor_id': docente.id,
        'programa_id': prog.id,
        'nivel': 'Secundaria',
        'grado': '7mo Grado',
        'seccion': 'B',
    }
    r_crear = c.post('/academico/programas/', post_data_crear, follow=True)
    assert r_crear.status_code == 200
    nueva_carga = CargaAcademica.objects.filter(profesor=docente, programa=prog, grado='7mo Grado', seccion='B').first()
    assert nueva_carga is not None, "Error: No se guardó la nueva carga académica"
    print(f"    [OK] Creación de nueva asignación exitosa (ID #{nueva_carga.id}): {prog.denominacion} - 7mo Grado B")

    # Editar la asignación recién creada
    post_data_editar = {
        'carga_id': nueva_carga.id,
        'profesor_id': docente.id,
        'programa_id': prog.id,
        'nivel': 'Secundaria',
        'grado': '8vo Grado',
        'seccion': 'A',
    }
    r_editar = c.post('/academico/programas/', post_data_editar, follow=True)
    assert r_editar.status_code == 200
    nueva_carga.refresh_from_db()
    assert nueva_carga.grado == '8vo Grado' and nueva_carga.seccion == 'A', "Error: No se actualizó la asignación"
    print(f"    [OK] Edición de asignación exitosa (ID #{nueva_carga.id}): Actualizada a 8vo Grado A")

    # Eliminar la asignación de prueba para mantener limpio el entorno
    r_del = c.post(f'/academico/carga/{nueva_carga.id}/eliminar/', follow=True)
    assert r_del.status_code == 200
    assert not CargaAcademica.objects.filter(id=nueva_carga.id).exists(), "Error: No se eliminó la asignación de prueba"
    print("    [OK] Eliminación limpia de asignación de prueba exitosa.")

    print("\n" + "=" * 70)
    print("¡TODAS LAS PRUEBAS OBLIGATORIAS PASARON CON ÉXITO AL 100%!")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
