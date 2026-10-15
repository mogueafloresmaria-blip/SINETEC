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
html_init = r1.content.decode('utf-8')
assert 'Enviar enlace de recuperación' in html_init, "No se encontró el botón 'Enviar enlace de recuperación'"
assert 'Volver al inicio de sesión' in html_init, "No se encontró el enlace 'Volver al inicio de sesión'"
assert 'Número de Identificación' in html_init, "No se encontró el campo 'Número de Identificación'"
print("   [OK] Página de recuperación responde 200 OK con elementos requeridos")

print("\n2. Probando número de identificación inventado/al azar ('999888777')...")
r_random = c.post('/recuperar-contrasena/', {'identificador': '999888777'})
assert r_random.status_code == 200, f"Error {r_random.status_code}"
html_random = r_random.content.decode('utf-8')
assert 'No se encontró ninguna cuenta registrada con el número de identificación' in html_random and '999888777' in html_random, "Falló: No mostró mensaje de error para cuenta inexistente"
assert 'Crear Nueva Contraseña Ahora' not in html_random, "Error: No debe mostrar botón de reset si no existe"
assert 'Enlace enviado exitosamente' not in html_random, "Error: No debe simular envío para cuenta inventada"
print("   [OK] Número al azar rechazado correctamente: No simula envío y muestra alerta de error clara")

print("\n3. Probando POST con usuario real 'admin'...")
r2 = c.post('/recuperar-contrasena/', {'identificador': 'admin'})
assert r2.status_code == 200, f"Error {r2.status_code}"
html = r2.content.decode('utf-8')
assert ('Se ha enviado el enlace de recuperación al correo registrado' in html or 'Cuenta localizada con éxito' in html), "No contiene mensaje de confirmación real"
assert 'Crear Nueva Contraseña Ahora' in html, "No contiene botón de reset directo"

m = re.search(r'href="(/recuperar-contrasena/confirmar/[^"]+)"', html)
assert m, "No se encontró el enlace de confirmación en el HTML"
reset_url = m.group(1)
print(f"   [OK] Enlace de confirmación generado para cuenta existente: {reset_url}")

print("\n4. Probando GET al enlace de confirmación...")
r3 = c.get(reset_url)
assert r3.status_code == 200, f"Error {r3.status_code}"
html3 = r3.content.decode('utf-8')
assert 'Guardar Nueva Contraseña' in html3, "No contiene formulario de nueva clave"
print("   [OK] Formulario de nueva contraseña cargado correctamente (token válido)")

print("\n5. Probando cambio de contraseña con contraseñas que no coinciden...")
r_mismatch = c.post(reset_url, {
    'nueva_contrasena': 'Clave1234',
    'confirmar_contrasena': 'OtraClave'
})
assert r_mismatch.status_code == 200
assert 'Las contraseñas no coinciden' in r_mismatch.content.decode('utf-8')
print("   [OK] Validación de coincidencia funcionando")

print("\n6. Probando cambio de contraseña exitoso...")
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

print("\n7. Probando reuso del token usado...")
r_reuso = c.get(reset_url)
assert r_reuso.status_code == 400, f"Esperado 400 por token caducado, obtenido {r_reuso.status_code}"
print("   [OK] El token de un solo uso fue invalidado correctamente (seguridad 100%)")

# Restaurar la clave de admin original para el entorno demo
user.set_password('12345')
user.save()
print("\n[ÉXITO TOTAL] Todas las pruebas pasaron satisfactoriamente. Clave demo de admin restaurada.")
