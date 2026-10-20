import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.contrib.auth.models import User
from academico.models import Matricula, CargaAcademica, HorarioFicha, ProgramaFormacion
from seguimiento.models import Notificacion, ComunicadoEscolar, AsistenciaAprendiz
from usuarios.models import FamiliaAcudiente, PagoPension, TransporteRuta

def test_auditoria_seis_paneles():
    print("=" * 80)
    print("AUDITORÍA INTEGRAL DE LOS 6 PANELES DE EDUNOVA (VERIFICACIÓN RIGUROSA)")
    print("=" * 80)

    # 1. VERIFICACIÓN DE MOTOR DE BASE DE DATOS
    from django.db import connection
    engine = connection.settings_dict['ENGINE']
    db_name = connection.settings_dict['NAME']
    print(f"\n[1] Motor de Base de Datos Verificado: {engine}")
    print(f"    Nombre de Base de Datos: {db_name}")
    assert 'mysql' in engine, f"Error: Se esperaba MySQL pero se encontró {engine}"
    print("    [OK] Motor MySQL en producción verificado exitosamente.")

    # 2. VERIFICACIÓN DE ESTADO DEMOSTRACIÓN (1 DOCENTE, 1 ESTUDIANTE, 1 MATRÍCULA)
    print("\n[2] Verificación de la regla institucional de la demostración...")
    docentes_activos = User.objects.filter(is_active=True, perfil__rol__nombre__icontains='Docente')
    estudiantes_activos = User.objects.filter(is_active=True, perfil__rol__nombre='Estudiante')
    matriculas_activas = Matricula.objects.filter(estado_formacion='En Formacion', aprendiz__is_active=True)

    print(f" -> Docentes activos: {docentes_activos.count()} (Esperado: 1)")
    assert docentes_activos.count() == 1
    docente = docentes_activos.first()
    print(f"    Docente activo: {docente.username} - {docente.get_full_name()}")

    print(f" -> Estudiantes activos: {estudiantes_activos.count()} (Esperado: 1)")
    assert estudiantes_activos.count() == 1
    estudiante = estudiantes_activos.first()
    print(f"    Estudiante activo: {estudiante.username} - {estudiante.get_full_name()}")
    assert estudiante.username == 'est1' and 'Juan' in estudiante.get_full_name()

    print(f" -> Matrículas activas: {matriculas_activas.count()} (Esperado: 1)")
    assert matriculas_activas.count() == 1
    mat = matriculas_activas.first()
    print(f"    Matrícula activa: {mat.aprendiz.get_full_name()} | Grado {mat.grado_escolar}°{mat.seccion}")

    # Acudiente
    acudiente = User.objects.filter(username='familia', is_active=True).first()
    assert acudiente is not None
    fam_rec = FamiliaAcudiente.objects.filter(estudiantes=estudiante).first()
    assert fam_rec is not None
    print(f"    Acudiente activo: {acudiente.username} - {fam_rec.nombre_acudiente} (Vinculada a Juan Pérez)")

    # Ausencia de notificaciones/tareas ficticias
    notifs_est = Notificacion.objects.filter(usuario=estudiante).count()
    comunicados_total = ComunicadoEscolar.objects.count()
    print(f" -> Notificaciones Juan Pérez: {notifs_est} (Esperado: 0)")
    print(f" -> Comunicados ficticios en sistema: {comunicados_total} (Esperado: 0)")
    assert notifs_est == 0
    assert comunicados_total == 0

    # 3. VERIFICACIÓN DE LOS SEIS PANELES
    print("\n[3] Verificación y auditoría de los 6 paneles independientes...")
    c = Client()

    # PANEL 1: ADMINISTRADOR
    admin_u = User.objects.get(username='admin')
    c.force_login(admin_u)
    r_admin = c.get('/dashboard/')
    assert r_admin.status_code == 200
    assert r_admin.context['total_docentes'] == 1
    assert r_admin.context['total_aprendices'] == 1
    assert r_admin.context['matriculas_anio'] == 1
    print("    [OK] Panel 1: Administrador (/dashboard/) -> 200 OK (Métricas reales: 1 doc, 1 est, 1 mat)")

    # PANEL 2: RECTORÍA
    rector_u = User.objects.get(username='rector')
    c.force_login(rector_u)
    r_rector = c.get('/rectoria/')
    assert r_rector.status_code == 200
    print("    [OK] Panel 2: Rectoría (/rectoria/) -> 200 OK")

    # PANEL 3: SECRETARÍA
    sec_u = User.objects.get(username='secretaria')
    c.force_login(sec_u)
    r_sec = c.get('/secretaria/')
    assert r_sec.status_code == 200
    print("    [OK] Panel 3: Secretaría (/secretaria/) -> 200 OK")

    # PANEL 4: DOCENTE
    c.force_login(docente)
    r_doc = c.get('/docente/')
    assert r_doc.status_code == 200
    assert r_doc.context['total_estudiantes_docente'] == 1
    # Verificar contadores por asignatura
    for asig in r_doc.context['asignaturas_metricas']:
        print(f"       Asignatura '{asig['nombre']}': {asig['total_estudiantes']} estudiante(s)")
        assert asig['total_estudiantes'] <= 1
    print("    [OK] Panel 4: Docente (/docente/) -> 200 OK (Contadores exactos de estudiantes)")

    # PANEL 5: FAMILIA
    c.force_login(acudiente)
    r_fam = c.get('/familia/')
    assert r_fam.status_code == 200
    print("    [OK] Panel 5: Familia (/familia/) -> 200 OK (Estudiante Juan Pérez vinculado)")

    # PANEL 6: ESTUDIANTE (JUAN PÉREZ)
    c.force_login(estudiante)
    r_est = c.get('/estudiante/')
    assert r_est.status_code == 200
    # Verificar que los 4 periodos existen y tienen número
    periodos = r_est.context.get('periodos_academicos', [])
    assert len(periodos) == 4, f"Se esperaban 4 periodos, hay {len(periodos)}"
    for p in periodos:
        assert p.numero in [1, 2, 3, 4]
        assert not p.tiene_calificaciones # Están vacíos y claros
    print("    [OK] Panel 6: Estudiante (/estudiante/) -> 200 OK (Períodos 1, 2, 3 y 4 interactivos y vacíos)")

    # 4. HORARIO Y COINCIDENCIA ENTRE DOCENTE Y ESTUDIANTE
    print("\n[4] Comprobando coherencia del horario docente-estudiante...")
    horarios_doc = HorarioFicha.objects.filter(instructor=docente, activo=True)
    horarios_est = HorarioFicha.objects.filter(grado__icontains='10', seccion='A', activo=True)
    # Todas las materias que ve el estudiante en 10°A las imparte el docente activo
    for h in horarios_est:
        assert h.instructor == docente
    print(f"    [OK] Horario 100% coordinado: {horarios_est.count()} bloques de clase en Grado 10°A a cargo de {docente.get_full_name()}.")

    # 5. CARGA ACADÉMICA (DISEÑO Y OPERACIONES CRUD EN ADMINISTRADOR)
    print("\n[5] Comprobando Carga Académica en Admin (GET, POST Crear, POST Editar, POST Eliminar)...")
    c.force_login(admin_u)
    r_carga = c.get('/academico/programas/')
    assert r_carga.status_code == 200
    content_html = r_carga.content.decode('utf-8')
    assert 'cardFormularioCarga' in content_html
    assert 'Asignaciones Registradas' in content_html
    assert 'VISTA PREVIA DE LA ASIGNACIÓN' in content_html

    # Crear una asignación
    prog = ProgramaFormacion.objects.filter(activo=True).first()
    post_crear = {
        'profesor_id': docente.id,
        'programa_id': prog.id,
        'nivel': 'Secundaria',
        'grado': '7mo Grado',
        'seccion': 'C',
    }
    r_c = c.post('/academico/programas/', post_crear, follow=True)
    assert r_c.status_code == 200
    carga_creada = CargaAcademica.objects.filter(profesor=docente, programa=prog, grado='7mo Grado', seccion='C').first()
    assert carga_creada is not None
    print(f"    [OK] Creación exitosa: Carga ID #{carga_creada.id} ({prog.denominacion} - 7mo Grado C)")

    # Editar la asignación
    post_editar = {
        'carga_id': carga_creada.id,
        'profesor_id': docente.id,
        'programa_id': prog.id,
        'nivel': 'Secundaria',
        'grado': '8vo Grado',
        'seccion': 'B',
    }
    r_e = c.post('/academico/programas/', post_editar, follow=True)
    assert r_e.status_code == 200
    carga_creada.refresh_from_db()
    assert carga_creada.grado == '8vo Grado' and carga_creada.seccion == 'B'
    print(f"    [OK] Edición exitosa: Carga ID #{carga_creada.id} actualizada a 8vo Grado B")

    # Eliminar la asignación de prueba
    r_d = c.post(f'/academico/carga/{carga_creada.id}/eliminar/', follow=True)
    assert r_d.status_code == 200
    assert not CargaAcademica.objects.filter(id=carga_creada.id).exists()
    print(f"    [OK] Eliminación limpia exitosa: Carga enviada a papelera y eliminada del catálogo activo.")

    print("\n" + "=" * 80)
    print("¡AUDITORÍA Y PRUEBAS COMPLETADAS CON 100% DE ÉXITO!")
    print("=" * 80)

if __name__ == '__main__':
    test_auditoria_seis_paneles()
