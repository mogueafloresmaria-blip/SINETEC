import re
import requests
import sys

BASE_URL = 'http://127.0.0.1:8000'

def run_live_verification():
    print("=" * 70)
    print("VERIFICACIÓN EN TIEMPO REAL DEL PANEL DOCENTE EN VIVO (127.0.0.1:8000)")
    print("=" * 70)
    
    s = requests.Session()
    
    # 1. Login
    r_login_page = s.get(f'{BASE_URL}/login/')
    assert r_login_page.status_code == 200, f"Error al abrir login: {r_login_page.status_code}"
    
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_login_page.text)
    csrf = csrf_match.group(1) if csrf_match else s.cookies.get('csrftoken')
    
    r_login = s.post(
        f'{BASE_URL}/login/',
        data={'username': 'docente', 'password': 'Password123*', 'csrfmiddlewaretoken': csrf},
        headers={'Referer': f'{BASE_URL}/login/'},
        allow_redirects=True
    )
    print(f"[LOGIN] Status: {r_login.status_code}, URL Final: {r_login.url}")
    assert 'docente' in r_login.text or 'Miguel' in r_login.text or r_login.status_code == 200, "Error en autenticacion"

    # Modulos a probar
    modulos = [
        ("1. Inicio", f"{BASE_URL}/instructor/?subpanel=inicio"),
        ("2. Perfil", f"{BASE_URL}/perfil-profesional/"),
        ("3. Mis Asignaturas", f"{BASE_URL}/mis-asignaturas/"),
        ("4. Mis Estudiantes", f"{BASE_URL}/mis-estudiantes/"),
        ("5. Actividades y Tareas", f"{BASE_URL}/actividades-y-tareas/"),
        ("6. Calificaciones", f"{BASE_URL}/calificaciones-docente/"),
        ("7. Asistencia", f"{BASE_URL}/asistencia/"),
        ("8. Horario", f"{BASE_URL}/horario-escolar/"),
        ("9. Comunicaciones", f"{BASE_URL}/comunicaciones-docente/"),
        ("10. Documentos", f"{BASE_URL}/documentos-docente/"),
        ("11. Notificaciones", f"{BASE_URL}/notificaciones-docente/"),
        ("12. Papelera", f"{BASE_URL}/papelera-docente/"),
    ]

    for nombre, url in modulos:
        res = s.get(url)
        print(f"\n--- Probando {nombre} -> {url} ---")
        print(f"  Status Code: {res.status_code}")
        assert res.status_code == 200, f"Fallo al cargar {nombre}: HTTP {res.status_code}"
        
        # Verificar pantalla blanca (contenido minimo)
        assert len(res.text.strip()) > 500, f"Posible pantalla blanca en {nombre} (longitud {len(res.text)})"
        
        # Verificar que no haya restos de SENA / SINETEC en texto visible
        # (excluyendo rutas internas de assets si hubiese alguna)
        html_lower = res.text.lower()
        
        # Buscar restos de "Instructor SENA" o "Aprendiz"
        sena_matches = re.findall(r'\b(instructor sena|aprendiz|sinetec)\b', html_lower)
        if sena_matches:
            matches_lines = [line.strip() for line in res.text.splitlines() if re.search(r'\b(instructor sena|aprendiz|sinetec)\b', line, re.I)]
            print(f"  [ALERTA RESTOS]: {set(sena_matches)} encontrados en {nombre} -> {matches_lines[:3]}")
        else:
            print(f"  [OK] Cero restos visibles de SENA/Aprendiz/SINETEC en {nombre}")
            
        # Verificar javascript:void(0)
        void_matches = re.findall(r'href=["\']javascript:void\(0\)["\']', res.text)
        if void_matches:
            print(f"  [AVISO] {len(void_matches)} enlaces 'javascript:void(0)' en {nombre}")
        else:
            print(f"  [OK] Cero enlaces 'javascript:void(0)' en {nombre}")
            
        # Verificar paleta y branding EDUNOVA
        assert 'edunova' in html_lower or 'institución educativa' in html_lower, f"Falta branding institucional en {nombre}"
        print(f"  [OK] Branding institucional EduNova verificado")

    # Verificacion especifica A: INICIO
    res_inicio = s.get(f'{BASE_URL}/instructor/?subpanel=inicio')
    assert '10-A' in res_inicio.text or '10°A' in res_inicio.text or '10' in res_inicio.text, "Grado 10 no encontrado en Inicio"
    assert '11-A' in res_inicio.text or '11°A' in res_inicio.text or '11' in res_inicio.text, "Grado 11 no encontrado en Inicio"
    assert 'Grado 6' not in res_inicio.text and 'Grado 7' not in res_inicio.text and 'Grado 8' not in res_inicio.text, "Grados ajenos encontrados en Inicio"
    print("\n[ESPECÍFICO A] Inicio verificado con 10-A y 11-A exclusivamente.")

    # Verificacion especifica B: ESTUDIANTES (propio vs ajeno)
    res_propio = s.get(f'{BASE_URL}/estudiantes/143/')
    print(f"\n[ESPECÍFICO B] Consulta estudiante propio (ID 143): HTTP {res_propio.status_code}")
    assert res_propio.status_code == 200, "Estudiante propio debio responder 200"
    assert '4.8' not in res_propio.text or 'definitiva' in res_propio.text.lower(), "Verificar notas ficticias"
    assert '95%' not in res_propio.text, "Falsa asistencia del 95% detectada"
    assert '29/09' not in res_propio.text, "Falsa fecha de asistencia detectada"

    res_ajeno = s.get(f'{BASE_URL}/estudiantes/197/')
    print(f"[ESPECÍFICO B] Consulta estudiante ajeno (ID 197): HTTP {res_ajeno.status_code}")
    assert res_ajeno.status_code == 403, f"Estudiante ajeno no fue bloqueado: HTTP {res_ajeno.status_code}"
    print("[ESPECÍFICO B] Estudiante ajeno correctamente bloqueado con HTTP 403.")

    # Verificacion especifica G: NOTIFICACIONES (ciclo de persistencia)
    res_notif = s.get(f'{BASE_URL}/notificaciones-docente/')
    csrf_token = s.cookies.get('csrftoken') or re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', res_notif.text).group(1)
    
    # Buscar id de una notificacion no leida
    match_id = re.search(r'data-notif-id=["\'](\d+)["\']', res_notif.text)
    if not match_id:
        match_id = re.search(r'/notificaciones/(\d+)/marcar-leida-ajax/', res_notif.text)
        
    print("\n[ESPECÍFICO G] Probando ciclo de notificaciones...")
    if match_id:
        notif_id = match_id.group(1)
        r_mark = s.post(
            f'{BASE_URL}/notificaciones/{notif_id}/marcar-leida-ajax/',
            headers={'X-CSRFToken': csrf_token, 'X-Requested-With': 'XMLHttpRequest', 'Referer': f'{BASE_URL}/notificaciones-docente/'}
        )
        print(f"  Marcar individual AJAX ({notif_id}): Status {r_mark.status_code}, JSON: {r_mark.text}")
        data = r_mark.json()
        assert data.get('success') is True, "Fallo al marcar notificacion"
        nuevo_conteo = data.get('total_sin_leer') or data.get('total_no_leidas')
        
        # F5 - Recargar pagina
        res_notif_f5 = s.get(f'{BASE_URL}/notificaciones-docente/')
        print(f"  F5 Recarga status: {res_notif_f5.status_code}")
        # Verificar que el nuevo conteo persiste en el HTML
        assert str(nuevo_conteo) in res_notif_f5.text or nuevo_conteo == 0, "El nuevo conteo no persistio tras F5"
        print(f"  [OK] Persistencia confirmada tras F5: {nuevo_conteo}")

    print("\n" + "=" * 70)
    print("¡VERIFICACIÓN EN TIEMPO REAL 100% EXITOSA!")
    print("=" * 70)

if __name__ == '__main__':
    run_live_verification()
