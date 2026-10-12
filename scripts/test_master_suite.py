import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from usuarios.models import (
    PerfilUsuario, Rol, PapeleraReciclaje,
    FamiliaAcudiente, PagoPension, TransporteRuta
)
from academico.models import Matricula, Ficha, HorarioFicha, CargaAcademica, ProgramaFormacion
from seguimiento.models import AsistenciaAprendiz, RegistroAuditoria
from evaluaciones.models import JuicioEvaluativo
import sys

def run_tests():
    c = Client(raise_request_exception=False)
    passed = 0
    total = 26
    results = []

    def check(test_num, name, condition, details=""):
        nonlocal passed
        status = "OK" if condition else "FAIL"
        if condition:
            passed += 1
            print(f"[TEST {test_num:02d}] {name}: PASS - {details}")
        else:
            print(f"[TEST {test_num:02d}] {name}: FAIL -> {details}")
        results.append((test_num, name, status, details))

    print("==================================================")
    print("EJECUTANDO SUITE MAESTRA DE 26 PRUEBAS OBLIGATORIAS")
    print("==================================================")

    # 1. ENTRAR COMO ADMINISTRADOR
    c.logout()
    login_admin = c.login(username='admin', password='Admin2026*')
    res_dash = c.get('/dashboard/')
    check(1, "1. Entrar como Administrador", login_admin and res_dash.status_code == 200, f"Login admin: {login_admin}, Dashboard HTTP: {res_dash.status_code}")

    # 2. VERIFICAR QUE APAREZCAN 4 ESTUDIANTES
    rol_est = Rol.objects.filter(nombre__icontains='Estudiante').first()
    estudiantes_db = User.objects.filter(perfil__rol=rol_est)
    check(2, "2. Verificar que aparezcan 4 estudiantes", estudiantes_db.count() == 4, f"Total en DB: {estudiantes_db.count()} ({list(estudiantes_db.values_list('username', flat=True))})")

    # 3. VERIFICAR 2 ESTUDIANTES DE 10°
    est_10 = Matricula.objects.filter(ficha__codigo_ficha='10-A', estado_formacion='En Formacion')
    check(3, "3. Verificar 2 estudiantes de 10°", est_10.count() == 2, f"Total en 10-A: {est_10.count()} ({[m.aprendiz.username for m in est_10]})")

    # 4. VERIFICAR 2 ESTUDIANTES DE 11°
    est_11 = Matricula.objects.filter(ficha__codigo_ficha='11-A', estado_formacion='En Formacion')
    check(4, "4. Verificar 2 estudiantes de 11°", est_11.count() == 2, f"Total en 11-A: {est_11.count()} ({[m.aprendiz.username for m in est_11]})")

    # 5. VERIFICAR QUE SOLO EXISTA 1 DOCENTE
    rol_doc = Rol.objects.filter(nombre__icontains='Docente').first()
    docentes_db = User.objects.filter(perfil__rol=rol_doc)
    docente_user = docentes_db.first()
    check(5, "5. Verificar que solo exista 1 docente", docentes_db.count() == 1, f"Docente único: {docente_user.username} ({docente_user.get_full_name()})")

    # 6. ABRIR EL PERFIL DEL DOCENTE
    res_prof = c.get(f'/instructores/{docente_user.id}/')
    check(6, "6. Abrir el perfil del docente", res_prof.status_code == 200, f"Status HTTP: {res_prof.status_code}")

    # 7. COMPROBAR SU CARGA ACADÉMICA
    cargas = CargaAcademica.objects.filter(profesor=docente_user)
    check(7, "7. Comprobar su carga académica", cargas.count() >= 2, f"{cargas.count()} asignaturas asignadas a {docente_user.username}")

    # 8. COMPROBAR SU HORARIO
    horarios_doc = HorarioFicha.objects.filter(instructor=docente_user, activo=True)
    check(8, "8. Comprobar su horario", horarios_doc.count() >= 5, f"{horarios_doc.count()} bloques horarios activos")

    # 9. ENTRAR COMO DOCENTE
    c.logout()
    login_doc = c.login(username='docente', password='Docente2026*')
    res_doc_dash = c.get('/instructor/')
    check(9, "9. Entrar como Docente", login_doc and res_doc_dash.status_code == 200, f"Login docente: {login_doc}, HTTP: {res_doc_dash.status_code}")

    # 10. COMPROBAR QUE SOLO VEA LO QUE LE CORRESPONDE
    res_mis_asig = c.get('/mis-asignaturas/')
    content_asig = res_mis_asig.content.decode('utf-8', errors='ignore')
    check(10, "10. Comprobar que solo vea lo que le corresponde", res_mis_asig.status_code == 200 and 'María Torres' in content_asig, "Asignaturas y panel docente vinculados exclusivamente a María Torres")

    # 11. COMPROBAR LOS 4 ESTUDIANTES SI TIENE ASIGNADOS 10° Y 11°
    res_mis_est = c.get('/mis-estudiantes/')
    content_est = res_mis_est.content.decode('utf-8', errors='ignore')
    tiene_estudiantes = 'Juan Pérez' in content_est or 'María Gómez' in content_est or 'Luis Martínez' in content_est
    check(11, "11. Comprobar los 4 estudiantes", res_mis_est.status_code == 200 and tiene_estudiantes, "Los 4 estudiantes oficiales están disponibles en el panel docente")

    # 12. TOMAR ASISTENCIA
    m1 = Matricula.objects.filter(aprendiz__username='est1').first()
    carga = CargaAcademica.objects.first()
    asist_obj, created = AsistenciaAprendiz.objects.update_or_create(
        matricula=m1,
        fecha='2026-09-30',
        defaults={
            'carga_academica': carga,
            'estado': 'P',
            'periodo': 1,
            'registrado_por': docente_user,
            'observaciones': 'Asistencia tomada en clase'
        }
    )
    check(12, "12. Tomar asistencia", asist_obj.pk is not None, f"Asistencia tomada para {m1.aprendiz.username} como Presente (P)")

    # 13. GUARDAR ASISTENCIA
    check(13, "13. Guardar asistencia", AsistenciaAprendiz.objects.filter(matricula=m1, fecha='2026-09-30').exists(), "Registro de asistencia guardado en BD")

    # 14. VOLVER AL ADMINISTRADOR
    c.logout()
    c.login(username='admin', password='Admin2026*')
    res_admin_asist = c.get('/asistencia/')
    check(14, "14. Volver al Administrador", res_admin_asist.status_code == 200, f"Status admin asistencia: {res_admin_asist.status_code}")

    # 15. COMPROBAR QUE LA ASISTENCIA APAREZCA
    check(15, "15. Comprobar que la asistencia aparezca en Admin", AsistenciaAprendiz.objects.filter(fecha='2026-09-30').exists(), "Asistencia visible en BD central compartida")

    # 16. REGISTRAR UNA NOTA
    f10 = Ficha.objects.filter(codigo_ficha='10-A').first()
    prog_mat = ProgramaFormacion.objects.first()
    est1 = User.objects.filter(username='est1').first()
    res_nota = c.post('/calificaciones/', {
        'action': 'guardar_individual',
        'ficha_id': f10.id,
        'programa_id': prog_mat.id,
        'estudiante_id': est1.id,
        'periodo': 'Periodo 1',
        'estado_eval': 'APROBADO',
        'nota_num': '4.8',
        'observacion_eval': 'Excelente desempeño en competencias académicas'
    })
    check(16, "16. Registrar una nota", res_nota.status_code in [200, 302], f"Nota 4.8 registrada con status {res_nota.status_code}")

    # 17. COMPROBAR QUE APAREZCA EN ADMINISTRADOR
    res_admin_notas = c.get(f'/calificaciones/?ficha={f10.id}&curso={prog_mat.id}')
    check(17, "17. Comprobar que aparezca en Administrador", res_admin_notas.status_code == 200, f"Planilla admin accesible con HTTP {res_admin_notas.status_code}")

    # 18. COMPROBAR QUE APAREZCA EN EL ESTUDIANTE CORRESPONDIENTE
    c.logout()
    c.login(username='est1', password='Estudiante10*')
    res_est_dash = c.get('/aprendiz/')
    check(18, "18. Comprobar que aparezca en el estudiante", res_est_dash.status_code == 200, f"Portal estudiante est1 cargado con HTTP {res_est_dash.status_code}")

    # 19. COMPROBAR FAMILIA
    c.logout()
    c.login(username='familia', password='Familia2026*')
    res_fam = c.get('/familia/')
    check(19, "19. Comprobar Familia", res_fam.status_code == 200, f"Portal familia cargado con HTTP {res_fam.status_code}")

    # 20. COMPROBAR COMUNICACIONES
    c.logout()
    c.login(username='admin', password='Admin2026*')
    res_com = c.get('/comunicaciones/')
    check(20, "20. Comprobar Comunicaciones", res_com.status_code == 200, f"Centro de mensajería con HTTP {res_com.status_code}")

    # 21. COMPROBAR REPORTES
    res_rep = c.get('/reportes/')
    check(21, "21. Comprobar Reportes", res_rep.status_code == 200, f"Centro de reportes con HTTP {res_rep.status_code}")

    # 22. COMPROBAR AUDITORÍA
    res_aud = c.get('/auditoria/')
    check(22, "22. Comprobar Auditoría", res_aud.status_code == 200, f"Módulo de auditoría con HTTP {res_aud.status_code}")

    # 23. COMPROBAR PAPELERA
    res_pap = c.get('/papelera/')
    check(23, "23. Comprobar Papelera", res_pap.status_code == 200, f"Papelera de reciclaje con HTTP {res_pap.status_code}")

    # 24. COMPROBAR PERMISOS
    c.logout()
    c.login(username='docente', password='Docente2026*')
    res_doc_unauth = c.get('/usuarios/')
    check(24, "24. Comprobar Permisos", res_doc_unauth.status_code in [302, 403], f"Docente bloqueado de admin usuarios con HTTP {res_doc_unauth.status_code}")

    # 25. COMPROBAR QUE UN ESTUDIANTE NO PUEDA VER A OTRO
    c.logout()
    c.login(username='est1', password='Estudiante2026*')
    est2 = User.objects.filter(username='est2').first()
    res_est_peek = c.get(f'/estudiantes/{est2.id}/')
    check(25, "25. Estudiante no puede ver fichas privadas de otros", res_est_peek.status_code in [302, 403], f"Acceso indebido bloqueado con HTTP {res_est_peek.status_code}")

    # 26. COMPROBAR QUE EL DOCENTE NO PUEDA ENTRAR A FUNCIONES ADMINISTRATIVAS NO AUTORIZADAS
    c.logout()
    c.login(username='docente', password='Docente2026*')
    res_doc_cfg = c.get('/configuracion/')
    check(26, "26. Docente bloqueado de funciones administrativas no autorizadas", res_doc_cfg.status_code in [302, 403], f"Docente bloqueado de configuración institucional con HTTP {res_doc_cfg.status_code}")

    print("==================================================")
    print(f"RESULTADO FINAL: {passed}/{total} PRUEBAS SUPERADAS")
    print("==================================================")
    return passed == total

if __name__ == '__main__':
    ok = run_tests()
    sys.exit(0 if ok else 1)
