# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import re

c = Client()

print("1. Probando GET /recuperar-contrasena/...")
r1 = c.get('/recuperar-contrasena/')
assert r1.status_code == 200, f"Error {r1.status_code}"
print("   [OK] Página de recuperación responde 200 OK")

print("\n2. Probando POST con identificador 'admin'...")
r2 = c.post('/recuperar-contrasena/', {'identificador': 'admin'})
assert r2.status_code == 200, f"Error {r2.status_code}"
html = r2.content.decode('utf-8')
assert 'Si existe una cuenta activa' in html, "No contiene mensaje de confirmación"
assert 'Crear Nueva Contraseña Ahora' in html, "No contiene botón de reset directo"

m = re.search(r'href="(/recuperar-contrasena/confirmar/[^"]+)"', html)
assert m, "No se encontró el enlace de confirmación en el HTML"
reset_url = m.group(1)
print(f"   [OK] Enlace de confirmación generado: {reset_url}")

print("\n3. Probando GET al enlace de confirmación...")
r3 = c.get(reset_url)
assert r3.status_code == 200, f"Error {r3.status_code}"
html3 = r3.content.decode('utf-8')
assert 'Guardar Nueva Contraseña' in html3, "No contiene formulario de nueva clave"
print("   [OK] Formulario de nueva contraseña cargado correctamente (token válido)")

print("\n4. Probando cambio de contraseña con contraseñas que no coinciden...")
r_mismatch = c.post(reset_url, {
    'nueva_contrasena': 'Clave1234',
    'confirmar_contrasena': 'OtraClave'
})
assert r_mismatch.status_code == 200
assert 'Las contraseñas no coinciden' in r_mismatch.content.decode('utf-8')
print("   [OK] Validación de coincidencia funcionando")

print("\n5. Probando cambio de contraseña exitoso...")
r_ok = c.post(reset_url, {
    'nueva_contrasena': 'ClaveAdmin2026',
    'confirmar_contrasena': 'ClaveAdmin2026'
})
assert r_ok.status_code == 302, f"Esperado 302 redirect, obtenido {r_ok.status_code}"
assert r_ok.url in ['/login/', '/accounts/login/'], f"Redirección a {r_ok.url}"
print(f"   [OK] Redirigido exitosamente a {r_ok.url}")

user = User.objects.get(username='admin')
assert user.check_password('ClaveAdmin2026'), "La contraseña no fue actualizada"
print("   [OK] Contraseña verificada en base de datos: ClaveAdmin2026 es VÁLIDA")

print("\n6. Probando reuso del token usado...")
r_reuso = c.get(reset_url)
assert r_reuso.status_code == 400, f"Esperado 400 por token caducado, obtenido {r_reuso.status_code}"
print("   [OK] El token de un solo uso fue invalidado correctamente (seguridad 100%)")

# Restaurar la clave de admin original para el entorno demo
user.set_password('12345')
user.save()
print("\n[ÉXITO TOTAL] El flujo de recuperación de contraseñas funciona al 100%. Clave demo restaurada a 12345.")
