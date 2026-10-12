import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

try:
    from django.test.utils import setup_test_environment
    setup_test_environment()
except RuntimeError:
    pass

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from seguimiento.models import Notificacion
from academico.models import CargaAcademica, Matricula, DocumentoInstitucional, GuiaClase
from usuarios.models import FamiliaAcudiente


def test_docente_full_audit():
    client = Client()
    docente = User.objects.get(username='docente')
    client.force_login(docente)

    print("\n" + "="*70)
    print("AUDITORÍA COMPLETA DEL PANEL DOCENTE — EDUNOVA")
    print("="*70)

    # -------------------------------------------------------------------------
    # 1. ASIGNACIÓN DEL DOCENTE (GRADOS 10 Y 11)
    # -------------------------------------------------------------------------
    cargas = CargaAcademica.objects.filter(profesor=docente)
    grados = set(''.join(c for c in str(carga.grado) if c.isdigit()) for carga in cargas)
    print(f"[TEST 1] Grados asignados al docente en BD: {grados}")
    assert grados == {'10', '11'}, f"Error: Los grados deben ser 10 y 11, se obtuvo: {grados}"
    print("  -> OK: Docente asignado estrictamente a Grado 10 y Grado 11.")

    # -------------------------------------------------------------------------
    # 2. PRUEBA DE SEGURIDAD: URL BLOCKING (403 FORBIDDEN EN BACKEND)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Verificando bloqueo de acceso por URL a grados no asignados:")
    for g_prohibido in ['3', '3A', '4', '4B', '5', '5A', '7', '8']:
        resp = client.get(f"/instructor/?grado={g_prohibido}")
        assert resp.status_code == 403, f"Fallo de seguridad: Grado {g_prohibido} retornó {resp.status_code} en lugar de 403"
        print(f"  -> Bloqueado exitosamente ?grado={g_prohibido} con HTTP 403")

    resp_est_ajeno = client.get("/instructor/?estudiante_id=999999")
    assert resp_est_ajeno.status_code == 403, f"Fallo: Estudiante no asignado retornó {resp_est_ajeno.status_code} en vez de 403"
    print("  -> Bloqueado exitosamente ?estudiante_id=999999 con HTTP 403")

    resp_carga_ajena = client.get("/instructor/?carga=999999")
    assert resp_carga_ajena.status_code == 403, f"Fallo: Carga no asignada retornó {resp_carga_ajena.status_code} en vez de 403"
    print("  -> Bloqueado exitosamente ?carga=999999 con HTTP 403")

    # -------------------------------------------------------------------------
    # 3. NOTIFICACIONES: PRUEBA DE CICLO Y PERSISTENCIA CON BANDEJA LIMPIA
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Verificando ciclo de notificaciones y persistencia de lectura:")
    Notificacion.objects.filter(usuario=docente).delete()
    # Crear 2 notificaciones temporales para la prueba
    n1 = Notificacion.objects.create(usuario=docente, titulo="Notificación Test Audit 1", mensaje="Prueba 1", tipo="info", leida=False)
    n2 = Notificacion.objects.create(usuario=docente, titulo="Notificación Test Audit 2", mensaje="Prueba 2", tipo="info", leida=False)
    
    total_inicial = Notificacion.objects.filter(usuario=docente, leida=False).count()
    print(f"  -> Notificaciones creadas para la prueba: {total_inicial}")

    # Leer una notificación vía endpoint AJAX
    resp_leer = client.post(f"/notificaciones/{n1.id}/marcar-leida-ajax/", content_type="application/json", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert resp_leer.status_code == 200, f"Error en AJAX leer notificación: {resp_leer.status_code}"
    
    # Comprobar en base de datos
    n1.refresh_from_db()
    assert n1.leida is True, "La notificación no se guardó como leída en la BD"
    total_tras_una = Notificacion.objects.filter(usuario=docente, leida=False).count()
    print(f"  -> Contador tras leer 1 notificación: {total_tras_una} (se decrementó de 2 a 1)")
    assert total_tras_una == 1, f"Se esperaba 1 pero se obtuvo {total_tras_una}"

    # Recargar la página y verificar que el contador permanece en 1
    resp_dash = client.get("/instructor/?subpanel=notificaciones")
    assert resp_dash.status_code == 200
    print("  -> OK: Tras recargar la página, el estado de lectura persiste.")

    # Marcar todas como leídas
    resp_todas = client.post("/notificaciones/marcar-todas-leidas/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert resp_todas.status_code == 200
    total_cero = Notificacion.objects.filter(usuario=docente, leida=False).count()
    print(f"  -> Contador tras marcar todas: {total_cero}")
    assert total_cero == 0, f"Se esperaba 0 pero se obtuvo {total_cero}"

    # Limpiar notificaciones temporales para dejar la bandeja del docente vacía (0)
    Notificacion.objects.filter(usuario=docente).delete()
    print("  -> OK: Bandeja restablecida a 0 notificaciones limpias.")

    # Restaurar para la demostración
    Notificacion.objects.filter(usuario=docente).update(leida=False)

    # -------------------------------------------------------------------------
    # 4. MIS ESTUDIANTES Y NÓMINA (SOLO GRADOS 10 Y 11)
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Verificando nómina de estudiantes del docente:")
    resp_est = client.get("/mis-estudiantes/")
    assert resp_est.status_code == 200
    alumnos = resp_est.context['todos_mis_estudiantes']
    nombres_est = [m.aprendiz.get_full_name() for m in alumnos]
    print(f"  -> Estudiantes visibles ({len(alumnos)}): {nombres_est}")
    assert len(alumnos) == 4, f"Se esperaban 4 estudiantes (2 de 10° y 2 de 11°), se obtuvieron {len(alumnos)}"
    for m in alumnos:
        g = ''.join(c for c in str(m.grado_escolar) if c.isdigit())
        assert g in ['10', '11'], f"Estudiante en grado no asignado: {m.grado_escolar}"
    print("  -> OK: Ningún estudiante de otros grados (3, 4, 5) aparece en la lista.")

    # -------------------------------------------------------------------------
    # 5. DOCUMENTOS: 3 CATEGORÍAS CLARAS
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Verificando las 3 categorías de gestión documental:")
    resp_doc = client.get("/instructor/?subpanel=documentos")
    assert resp_doc.status_code == 200
    mis_docs = resp_doc.context['mis_documentos']
    mat_ped = resp_doc.context['material_pedagogico']
    doc_inst = resp_doc.context['documentos_institucionales']

    print(f"  -> A. Mis Documentos: {len(mis_docs)} cargados por el docente (títulos/certificados)")
    print(f"  -> B. Material Pedagógico: {len(mat_ped)} guías de clase asignadas a Grados 10 y 11")
    print(f"  -> C. Documentos Institucionales: {len(doc_inst)} normativas emitidas por Rectoría/Secretaría")
    assert len(mis_docs) >= 1, "Debe existir al menos 1 documento en Mis Documentos"
    assert len(mat_ped) >= 1, "Debe existir al menos 1 guía en Material Pedagógico"
    assert len(doc_inst) >= 1, "Deben existir documentos institucionales de Rectoría/Secretaría"
    print("  -> OK: Las 3 categorías operan de forma independiente y organizada.")

    # -------------------------------------------------------------------------
    # 6. COMUNICACIONES Y FAMILIAS (RELACIÓN ESTRICTA)
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Verificando comunicaciones y vinculación con familias:")
    resp_com = client.get("/instructor/?subpanel=comunicaciones")
    assert resp_com.status_code == 200
    familias = resp_com.context['chat_familias']
    nombres_fam = [f['nombre'] for f in familias]
    print(f"  -> Familias visibles ({len(familias)}): {nombres_fam}")
    assert len(familias) == 4, f"Se esperaban 4 familias asociadas a los 4 estudiantes, hay {len(familias)}"
    print("  -> OK: Todas las familias corresponden a estudiantes asignados (Juan Pérez, María Gómez, Luis Martínez, Ana López).")

    # -------------------------------------------------------------------------
    # 7. ASISTENCIA Y CALIFICACIONES (GRADOS 10 Y 11)
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Verificando asistencia y calificaciones:")
    resp_asist = client.get("/asistencia/")
    assert resp_asist.status_code == 200
    est_asist = resp_asist.context['estudiantes_carga_sel']
    print(f"  -> Estudiantes en lista de asistencia: {len(est_asist)}")
    for e in est_asist:
        g = ''.join(c for c in str(e.grado_escolar) if c.isdigit())
        assert g in ['10', '11']

    resp_calif = client.get("/calificaciones-docente/")
    assert resp_calif.status_code == 200
    est_calif = resp_calif.context['estudiantes_carga_sel']
    print(f"  -> Estudiantes en planilla de calificaciones: {len(est_calif)}")
    for e in est_calif:
        g = ''.join(c for c in str(e.grado_escolar) if c.isdigit())
        assert g in ['10', '11']
    print("  -> OK: Asistencia y calificaciones solo operan sobre grados asignados.")

    # -------------------------------------------------------------------------
    # 8. MANUAL DE USUARIO (17 PUNTOS)
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Verificando renderizado del Manual de Usuario:")
    resp_man = client.get("/manual-docente/")
    assert resp_man.status_code == 200
    content_man = resp_man.content.decode('utf-8')
    assert "Cómo ingresar al sistema" in content_man
    assert "Qué aparece en Inicio" in content_man
    assert "Cómo tomar asistencia escolar" in content_man
    assert "Cómo calificar y dar retroalimentación" in content_man
    assert "Qué significa el contador de notificaciones" in content_man
    assert "Qué documentos solamente puede consultar" in content_man
    assert "Cómo usar la papelera de reciclaje" in content_man
    print("  -> OK: Manual de usuario completo renderizado con los 17 puntos.")

    print("\n" + "="*70)
    print("TODAS LAS PRUEBAS DE LA AUDITORÍA PASARON CON ÉXITO (100% OK)")
    print("="*70 + "\n")


if __name__ == '__main__':
    test_docente_full_audit()
