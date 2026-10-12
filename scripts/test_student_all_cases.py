import requests
import re
import sys

BASE_URL = 'http://127.0.0.1:8000'

casos = [
    ('Documento como usuario y password', '1001001001', '1001001001', None),
    ('Username est1 y documento como password', 'est1', '1001001001', None),
    ('Palabra estudiante y documento', 'estudiante', '1001001001', None),
    ('Palabra estudiante y 12345', 'estudiante', '12345', None),
    ('Documento y 12345', '1001001001', '12345', None),
    ('Username est1 y 12345', 'est1', '12345', None),
    ('Demo access student button', '', '', 'student'),
    ('Estudiante 2 (1001001002)', '1001001002', '1001001002', None),
    ('Estudiante 3 (1001001003)', '1001001003', '1001001003', None),
    ('Estudiante 4 (1001001004)', '1001001004', '1001001004', None),
]

all_passed = True

print("=" * 75)
print("VERIFICACIÓN DE TODOS LOS MODOS DE INGRESO PARA ESTUDIANTE")
print("=" * 75)

for desc, u, p, demo in casos:
    s = requests.Session()
    r_lp = s.get(f'{BASE_URL}/login/')
    csrf = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', r_lp.text).group(1)
    data = {'csrfmiddlewaretoken': csrf}
    if demo:
        data['demo_access'] = demo
    else:
        data['username'] = u
        data['password'] = p
    r_post = s.post(f'{BASE_URL}/login/', data=data, headers={'Referer': f'{BASE_URL}/login/'}, allow_redirects=True)
    final_url = r_post.url.replace(BASE_URL, '')
    ok = (r_post.status_code == 200 and '/login/' not in final_url and ('aprendiz' in final_url or 'estudiante' in final_url))
    status_str = '[OK]' if ok else '[FALLO]'
    if not ok:
        all_passed = False
    print(f"{status_str} {desc:42s} -> URL: {final_url} (HTTP {r_post.status_code})")

print("=" * 75)
if all_passed:
    print("¡TODOS LOS MODOS DE ACCESO DE ESTUDIANTE FUNCIONAN AL 100%!")
else:
    print("ALGUNOS MODOS DE ACCESO FALLARON.")
print("=" * 75)

sys.exit(0 if all_passed else 1)
