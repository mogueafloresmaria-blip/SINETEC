import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User


def verificar():
    print("\n========================================================")
    print("EJECUTANDO BATERÍA DE PRUEBAS DE SEGURIDAD Y VISTAS SINETEC")
    print("========================================================")

    client = Client()

    # 1. Página de inicio pública
    res_home = client.get('/')
    assert res_home.status_code == 200, f"Error en /: {res_home.status_code}"
    print("[OK] GET / (Landing Home) -> 200 OK")

    # 2. Verificar Aprendiz Demo
    print("\n[TEST PERFIL APRENDIZ]")
    assert client.login(username="aprendiz_demo", password="Sena2026*"), "Fallo login aprendiz_demo"
    print("[OK] Login aprendiz_demo -> Éxito")

    res_dash = client.get('/dashboard/')
    assert res_dash.status_code == 302 and '/aprendiz/' in res_dash.url, f"Error redirección dashboard aprendiz: {res_dash.url}"
    print("[OK] Dispatcher /dashboard/ -> Redirige a /aprendiz/ (302)")

    res_apr = client.get('/aprendiz/')
    assert res_apr.status_code == 200, f"Error en /aprendiz/: {res_apr.status_code}"
    print("[OK] GET /aprendiz/ -> 200 OK")

    # Bug 1 verification: Portafolio
    res_porta = client.get('/portafolio/')
    assert res_porta.status_code == 200, f"Error en /portafolio/ (list.count): {res_porta.status_code}"
    print("[OK] GET /portafolio/ -> 200 OK (Bug list.count() resuelto)")

    # RBAC security: Aprendiz NO puede acceder a coordinación ni administración
    res_coord_forbidden = client.get('/coordinacion/')
    assert res_coord_forbidden.status_code in [302, 403], f"Violación RBAC: Aprendiz accedió a /coordinacion/ ({res_coord_forbidden.status_code})"
    print("[OK] GET /coordinacion/ como Aprendiz -> BLOQUEADO (302/403 RBAC Activo)")

    res_usr_forbidden = client.get('/usuarios/')
    assert res_usr_forbidden.status_code in [302, 403], f"Violación RBAC: Aprendiz accedió a /usuarios/ ({res_usr_forbidden.status_code})"
    print("[OK] GET /usuarios/ como Aprendiz -> BLOQUEADO (302/403 RBAC Activo)")

    res_aud_forbidden = client.get('/auditoria/')
    assert res_aud_forbidden.status_code in [302, 403], f"Violación RBAC: Aprendiz accedió a /auditoria/ ({res_aud_forbidden.status_code})"
    print("[OK] GET /auditoria/ como Aprendiz -> BLOQUEADO (302/403 RBAC Activo)")

    client.logout()

    # 3. Verificar Instructor Demo
    print("\n[TEST PERFIL INSTRUCTOR]")
    assert client.login(username="instructor_demo", password="Sena2026*"), "Fallo login instructor_demo"
    print("[OK] Login instructor_demo -> Éxito")

    res_dash_inst = client.get('/dashboard/')
    assert res_dash_inst.status_code == 302 and '/instructor/' in res_dash_inst.url, f"Error redirección dashboard instructor: {res_dash_inst.url}"
    print("[OK] Dispatcher /dashboard/ -> Redirige a /instructor/ (302)")

    res_inst = client.get('/instructor/')
    assert res_inst.status_code == 200, f"Error en /instructor/: {res_inst.status_code}"
    print("[OK] GET /instructor/ -> 200 OK")

    res_eval = client.get('/evaluaciones/')
    assert res_eval.status_code == 200, f"Error en /evaluaciones/: {res_eval.status_code}"
    print("[OK] GET /evaluaciones/ -> 200 OK")

    # RBAC security: Instructor NO puede acceder a gestión de usuarios ni auditoría
    res_usr_inst = client.get('/usuarios/')
    assert res_usr_inst.status_code in [302, 403], f"Violación RBAC: Instructor accedió a /usuarios/ ({res_usr_inst.status_code})"
    print("[OK] GET /usuarios/ como Instructor -> BLOQUEADO (302/403 RBAC Activo)")

    client.logout()

    # 4. Verificar Secretaría Demo
    print("\n[TEST PERFIL SECRETARÍA]")
    assert client.login(username="secretaria_demo", password="Sena2026*"), "Fallo login secretaria_demo"
    print("[OK] Login secretaria_demo -> Éxito")

    res_dash_sec = client.get('/dashboard/')
    assert res_dash_sec.status_code == 302 and '/secretaria/' in res_dash_sec.url, f"Error redirección dashboard secretaría: {res_dash_sec.url}"
    print("[OK] Dispatcher /dashboard/ -> Redirige a /secretaria/ (302)")

    res_sec = client.get('/secretaria/')
    assert res_sec.status_code == 200, f"Error en /secretaria/: {res_sec.status_code}"
    print("[OK] GET /secretaria/ -> 200 OK")

    res_tram = client.get('/seguimiento/secretaria/')
    assert res_tram.status_code == 200, f"Error en /seguimiento/secretaria/: {res_tram.status_code}"
    print("[OK] GET /seguimiento/secretaria/ -> 200 OK")

    # RBAC security: Secretaría NO puede entrar a panel de coordinación
    res_coord_sec = client.get('/coordinacion/')
    assert res_coord_sec.status_code in [302, 403], f"Violación RBAC: Secretaría accedió a /coordinacion/ ({res_coord_sec.status_code})"
    print("[OK] GET /coordinacion/ como Secretaría -> BLOQUEADO (302/403 RBAC Activo)")

    client.logout()

    # 5. Verificar Coordinador Demo
    print("\n[TEST PERFIL COORDINADOR]")
    assert client.login(username="coordinador_demo", password="Sena2026*"), "Fallo login coordinador_demo"
    print("[OK] Login coordinador_demo -> Éxito")

    res_dash_coord = client.get('/dashboard/')
    assert res_dash_coord.status_code == 302 and '/coordinacion/' in res_dash_coord.url, f"Error redirección dashboard coordinador: {res_dash_coord.url}"
    print("[OK] Dispatcher /dashboard/ -> Redirige a /coordinacion/ (302)")

    res_coord = client.get('/coordinacion/')
    assert res_coord.status_code == 200, f"Error en /coordinacion/: {res_coord.status_code}"
    print("[OK] GET /coordinacion/ -> 200 OK")

    res_usr = client.get('/usuarios/')
    assert res_usr.status_code == 200, f"Error en /usuarios/: {res_usr.status_code}"
    print("[OK] GET /usuarios/ -> 200 OK")

    res_aud = client.get('/auditoria/')
    assert res_aud.status_code == 200, f"Error en /auditoria/: {res_aud.status_code}"
    print("[OK] GET /auditoria/ -> 200 OK")

    res_ep = client.get('/etapa-productiva/')
    assert res_ep.status_code == 200, f"Error en /etapa-productiva/: {res_ep.status_code}"
    print("[OK] GET /etapa-productiva/ -> 200 OK")

    res_inno = client.get('/innovacion/')
    assert res_inno.status_code == 200, f"Error en /innovacion/: {res_inno.status_code}"
    print("[OK] GET /innovacion/ -> 200 OK")

    res_doc = client.get('/documentos/')
    assert res_doc.status_code == 200, f"Error en /documentos/: {res_doc.status_code}"
    print("[OK] GET /documentos/ -> 200 OK")

    res_alt = client.get('/alertas/')
    assert res_alt.status_code == 200, f"Error en /alertas/: {res_alt.status_code}"
    print("[OK] GET /alertas/ -> 200 OK")

    client.logout()

    print("\n========================================================")
    print("TODAS LAS PRUEBAS DE VERIFICACIÓN PASARON EXITOSAMENTE (100%)")
    print("========================================================\n")


if __name__ == '__main__':
    verificar()
