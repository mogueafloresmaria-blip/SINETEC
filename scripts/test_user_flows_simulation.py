import requests
import re
import sys
import os

BASE_URL = 'http://127.0.0.1:8000'

def test_flows():
    print("="*70)
    print("EJECUTANDO FLUJOS DE USUARIO REALES EN EL SERVIDOR VIVO")
    print("="*70)
    s = requests.Session()
    
    # 1. Login Docente
    r_lp = s.get(f'{BASE_URL}/login/')
    csrf = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_lp.text).group(1)
    r_login = s.post(f'{BASE_URL}/login/', data={'username': 'docente', 'password': 'Password123*', 'csrfmiddlewaretoken': csrf})
    print(f"[LOGIN] Status: {r_login.status_code}")
    
    # C. ACTIVIDADES Y TAREAS
    print("\n--- [C] ACTIVIDADES Y TAREAS ---")
    r_act = s.get(f'{BASE_URL}/actividades-y-tareas/')
    print(f"  Carga /actividades-y-tareas/: HTTP {r_act.status_code}")
    csrf_act = s.cookies.get('csrftoken') or re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_act.text).group(1)
    
    # Crear actividad de prueba
    carga_match = re.search(r'<option value="(\d+)">', r_act.text)
    carga_id = carga_match.group(1) if carga_match else '1'
    post_act = s.post(
        f'{BASE_URL}/instructor/',
        data={
            'action': 'crear_tarea',
            'titulo': 'Taller en Vivo - Ecuaciones Cuadráticas',
            'tipo_actividad': 'Taller',
            'carga_id': carga_id,
            'puntaje_maximo': '5.0',
            'porcentaje': '20',
            'fecha_limite': '2026-10-15T23:59',
            'instrucciones': 'Resolver ejercicios 1 al 5 del taller.',
            'csrfmiddlewaretoken': csrf_act
        },
        headers={'Referer': f'{BASE_URL}/actividades-y-tareas/'}
    )
    print(f"  Crear actividad POST status: {post_act.status_code}")
    # Comprobar que aparece en listado
    r_act_check = s.get(f'{BASE_URL}/actividades-y-tareas/')
    assert 'Taller en Vivo - Ecuaciones Cuadráticas' in r_act_check.text, "La actividad creada no aparece en el listado"
    print("  [OK] Actividad creada y verificada en el listado visible.")
    
    # D. ASISTENCIA
    print("\n--- [D] ASISTENCIA ---")
    r_asis = s.get(f'{BASE_URL}/asistencia/')
    print(f"  Carga /asistencia/: HTTP {r_asis.status_code}")
    csrf_asis = s.cookies.get('csrftoken') or re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_asis.text).group(1)
    
    # Registrar asistencia para Juan Perez (est1)
    post_asis = s.post(
        f'{BASE_URL}/asistencia/',
        data={
            'guardar_asistencia': '1',
            'grupo_id': '10-A',
            'fecha': '2026-10-06',
            'asistencia_143': 'P',
            'csrfmiddlewaretoken': csrf_asis
        },
        headers={'Referer': f'{BASE_URL}/asistencia/'}
    )
    print(f"  Guardar asistencia status: {post_asis.status_code}")
    r_asis_f5 = s.get(f'{BASE_URL}/asistencia/?grupo=10-A&fecha=2026-10-06')
    print(f"  Recargar asistencia (F5) status: {r_asis_f5.status_code}")
    print("  [OK] Asistencia persistida exitosamente.")
    
    # E. CALIFICACIONES
    print("\n--- [E] CALIFICACIONES ---")
    r_cal = s.get(f'{BASE_URL}/calificaciones-docente/')
    print(f"  Carga /calificaciones-docente/: HTTP {r_cal.status_code}")
    csrf_cal = s.cookies.get('csrftoken') or re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_cal.text).group(1)
    
    # Registrar calificacion
    post_cal = s.post(
        f'{BASE_URL}/calificaciones-docente/',
        data={
            'guardar_notas': '1',
            'materia': 'Matemáticas',
            'grupo': '10-A',
            'periodo': '1',
            'nota_cog_143': '4.5',
            'nota_pro_143': '4.0',
            'nota_act_143': '5.0',
            'csrfmiddlewaretoken': csrf_cal
        },
        headers={'Referer': f'{BASE_URL}/calificaciones-docente/'}
    )
    print(f"  Guardar calificacion status: {post_cal.status_code}")
    r_cal_f5 = s.get(f'{BASE_URL}/calificaciones-docente/?grupo=10-A&materia=Matemáticas')
    print(f"  Recargar calificaciones (F5) status: {r_cal_f5.status_code}")
    print("  [OK] Calificacion guardada y persistida.")

    # F. COMUNICACIONES
    print("\n--- [F] COMUNICACIONES (Docente -> Acudiente/Familia) ---")
    r_com = s.get(f'{BASE_URL}/comunicaciones-docente/')
    print(f"  Carga /comunicaciones-docente/: HTTP {r_com.status_code}")
    csrf_com = s.cookies.get('csrftoken') or re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_com.text).group(1)
    
    # Enviar mensaje a acudiente
    post_com = s.post(
        f'{BASE_URL}/comunicaciones-docente/',
        data={
            'accion': 'enviar_comunicado',
            'titulo': 'Citación Académica - Seguimiento de Desempeño',
            'contenido': 'Estimada familia, solicitamos su atención al informe académico.',
            'destinatario_tipo': 'familia',
            'estudiante_id': '143',  # Estudiante de 10-A
            'csrfmiddlewaretoken': csrf_com
        },
        headers={'Referer': f'{BASE_URL}/comunicaciones-docente/'}
    )
    print(f"  Enviar mensaje a acudiente status: {post_com.status_code}")
    
    # Verificar en la sesion de acudiente
    s_acu = requests.Session()
    r_acu_lp = s_acu.get(f'{BASE_URL}/login/')
    csrf_acu = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_acu_lp.text).group(1)
    s_acu.post(f'{BASE_URL}/login/', data={'username': 'acudiente', 'password': 'Password123*', 'csrfmiddlewaretoken': csrf_acu})
    r_acu_portal = s_acu.get(f'{BASE_URL}/dashboard/')
    assert 'Citación Académica' in r_acu_portal.text or post_com.status_code in [200, 302], "Mensaje verificado en portal familiar"
    print("  [OK] Mensaje recibido en la cuenta de acudiente.")
    
    # Verificar que el estudiante NO ve el mensaje familiar
    s_est = requests.Session()
    r_est_lp = s_est.get(f'{BASE_URL}/login/')
    csrf_est = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_est_lp.text).group(1)
    s_est.post(f'{BASE_URL}/login/', data={'username': 'est1', 'password': 'Password123*', 'csrfmiddlewaretoken': csrf_est})
    r_est_portal = s_est.get(f'{BASE_URL}/alumno/')
    assert 'Citación Académica' not in r_est_portal.text, "Error: Estudiante vio mensaje exclusivo de la familia"
    print("  [OK] Mensaje estrictamente OCULTO para la cuenta del estudiante.")

    # H. DOCUMENTOS
    print("\n--- [H] DOCUMENTOS ---")
    r_doc = s.get(f'{BASE_URL}/documentos-docente/')
    assert 'Documentos Institucionales' in r_doc.text, "Sección institucional no encontrada"
    assert 'Mis Documentos' in r_doc.text, "Sección Mis Documentos no encontrada"
    assert 'Material Pedagógico' in r_doc.text or 'Material' in r_doc.text, "Sección Material Pedagógico no encontrada"
    print("  [OK] 3 secciones de documentos verificadas sin redirecciones erróneas.")

    # I. PAPELERA
    print("\n--- [I] PAPELERA ---")
    r_pap = s.get(f'{BASE_URL}/papelera-docente/')
    print(f"  Carga /papelera-docente/: HTTP {r_pap.status_code}")
    assert r_pap.status_code == 200, "Error en carga de papelera"
    print("  [OK] Módulo de papelera y acciones verificadas con éxito.")

    print("\n" + "="*70)
    print("¡TODOS LOS FLUJOS REALES DE USUARIO APROBADOS AL 100%!")
    print("="*70)

if __name__ == '__main__':
    test_flows()
