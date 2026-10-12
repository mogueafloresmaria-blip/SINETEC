import requests
import re
import sys

BASE_URL = 'http://127.0.0.1:8000'

def test_single_login(identifier, password, label_rol):
    s = requests.Session()
    # 1. Obtener token CSRF
    r_page = s.get(f'{BASE_URL}/login/')
    csrf_match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_page.text)
    csrf = csrf_match.group(1) if csrf_match else s.cookies.get('csrftoken')
    
    # 2. Enviar login POST
    r_login = s.post(
        f'{BASE_URL}/login/',
        data={'username': identifier, 'password': password, 'csrfmiddlewaretoken': csrf},
        headers={'Referer': f'{BASE_URL}/login/'},
        allow_redirects=True
    )
    
    # 3. Analizar respuesta
    final_url = r_login.url.replace(BASE_URL, '')
    is_success = r_login.status_code == 200 and '/login/' not in final_url
    
    return {
        'usuario': identifier,
        'password': password,
        'rol_esperado': label_rol,
        'status_code': r_login.status_code,
        'url_final': final_url,
        'exito': is_success,
        'html_title': re.search(r'<title>(.*?)</title>', r_login.text).group(1) if re.search(r'<title>(.*?)</title>', r_login.text) else 'Sin título'
    }

def main():
    print("=" * 80)
    print("VERIFICACIÓN REAL DE ACCESOS Y REDIRECCIÓN POR ROL (HTTP LIVE 127.0.0.1:8000)")
    print("=" * 80)

    pruebas = [
        ('admin', '12345', 'Administrador', '/dashboard/'),
        ('rector', '12345', 'Rectoría', '/rectoria/'),
        ('secretaria', '12345', 'Secretaría', '/secretaria/'),
        ('docente', '12345', 'Docente', '/instructor/'),
        ('familia', '12345', 'Familia', '/familia/'),
        ('acudiente', '12345', 'Familia/Acudiente', '/familia/'),
        ('1001001001', '1001001001', 'Estudiante (Login por Documento)', '/aprendiz/'),
        ('est1', '1001001001', 'Estudiante (Login por Username)', '/aprendiz/'),
        ('1001001002', '1001001002', 'Estudiante 2 (Login por Documento)', '/aprendiz/'),
    ]

    todos_ok = True
    resultados = []

    for usuario, clave, rol, url_esperada in pruebas:
        res = test_single_login(usuario, clave, rol)
        resultados.append(res)
        cumple_url = res['url_final'].startswith(url_esperada) or url_esperada in res['url_final']
        status_txt = "OK - EXITOSO" if (res['exito'] and cumple_url) else "ERROR - FALLIDO"
        if not (res['exito'] and cumple_url):
            todos_ok = False
            
        print(f"\n[{status_txt}] Rol: {rol}")
        print(f"  - Usuario probado : {res['usuario']}")
        print(f"  - Contraseña usada: {res['password']}")
        print(f"  - URL esperada    : {url_esperada}")
        print(f"  - URL final       : {res['url_final']} (HTTP {res['status_code']})")
        print(f"  - Título página   : {res['html_title'].strip()}")

    print("\n" + "=" * 80)
    if todos_ok:
        print("¡TODAS LAS PRUEBAS DE ACCESO POR ROL PASARON CON 100% DE ÉXITO!")
    else:
        print("ALGUNAS PRUEBAS DE ACCESO FALLARON.")
    print("=" * 80)

    return 0 if todos_ok else 1

if __name__ == '__main__':
    sys.exit(main())
