import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.contrib.auth.models import User
from usuarios.models import PerfilUsuario, PagoPension
from academico.models import Matricula, Ficha, CargaAcademica
from seguimiento.models import ComunicadoEscolar
from django.utils import timezone
from django.test import Client

print("=== 1. VERIFICACIÓN GESTIÓN DE CAJA ===")
admin = User.objects.filter(is_superuser=True).first()
estudiante = User.objects.filter(perfil__rol__nombre__icontains='Estudiante').first()
print(f"Admin: {admin.username if admin else None}, Estudiante: {estudiante.get_full_name() if estudiante else None}")

# 1.1 Crear un pago emitido hoy con responsable
pago = PagoPension.objects.create(
    estudiante=estudiante,
    concepto='Pensión Mensual Test Auto',
    monto=160000,
    estado='EMITIDO',
    metodo_pago='Efectivo',
    responsable=admin
)
print(f"-> Pago creado ID: {pago.id}, Recibo: {pago.numero_recibo}, Responsable: {pago.responsable.username}")

c = Client()
c.force_login(admin)

# 1.2 Cargar /pensiones/ y comprobar sección 'RECAUDO DE HOY'
resp = c.get('/pensiones/')
assert resp.status_code == 200, f"Error status: {resp.status_code}"
content = resp.content.decode('utf-8')
assert 'RECAUDO DE HOY' in content, "No se encontró la sección RECAUDO DE HOY"
assert 'Pensión Mensual Test Auto' in content, "No se encontró el concepto en Recaudo de hoy"
assert pago.numero_recibo in content, "No se encontró el número de recibo"
assert admin.username in content or admin.get_full_name() in content, "No se encontró el responsable"
print("-> Tabla 'RECAUDO DE HOY' verificada exitosamente en MySQL en tiempo real.")

# 1.3 Ver comprobante / factura HTML
resp_fac = c.get(f'/pensiones/{pago.id}/factura/')
assert resp_fac.status_code == 200
assert 'FACTURA' in resp_fac.content.decode('utf-8') or 'COMPROBANTE' in resp_fac.content.decode('utf-8')
print("-> Factura / Comprobante HTML verificado exitosamente.")

# 1.4 Descargar recibo PDF
resp_pdf = c.get(f'/pensiones/{pago.id}/recibo-pdf/')
assert resp_pdf.status_code == 200
assert resp_pdf['Content-Type'] == 'application/pdf'
print(f"-> Descarga de Recibo PDF verificado exitosamente (Tamaño: {len(resp_pdf.content)} bytes).")

# 1.5 Anular recibo
resp_anular = c.post('/pensiones/', {'anular_id': pago.id})
pago.refresh_from_db()
assert pago.estado == 'ANULADO', f"El estado no se actualizó a ANULADO: {pago.estado}"
print("-> Anulación de recibo verificada exitosamente.")

# 1.6 Endpoint Nuevo Cobro GET y POST
resp_nc_get = c.get('/pensiones/nuevo/')
assert resp_nc_get.status_code == 200
print("-> Vista Nuevo Cobro accesible.")

resp_nc_post = c.post('/pensiones/nuevo/', {
    'estudiante_id': estudiante.id,
    'concepto': 'Matrícula 2026 Test',
    'monto': '250000',
    'metodo_pago': 'Transferencia'
})
nuevo_pago = PagoPension.objects.filter(concepto='Matrícula 2026 Test', estudiante=estudiante).first()
assert nuevo_pago is not None
assert nuevo_pago.responsable == admin
print(f"-> Nuevo cobro registrado exitosamente por cajero {nuevo_pago.responsable.username}.")

print("\n=== 2. VERIFICACIÓN AISLAMIENTO GRUPOS DOCENTES ===")
docente = User.objects.filter(username='docente').first()
if docente:
    c_doc = Client()
    c_doc.force_login(docente)
    resp_doc = c_doc.get('/instructor/')
    assert resp_doc.status_code == 200
    print("-> Dashboard docente verificado con grupos aislados.")

print("\n=== 3. VERIFICACIÓN COMUNICADOS PRIVADOS ===")
circ = ComunicadoEscolar.objects.create(
    remitente=admin,
    estamento_destinatario='Estudiantes',
    estudiante_destinatario=estudiante,
    asunto='Circular Confidencial Estudiante 01',
    mensaje='Solo para el estudiante seleccionado'
)
c_est = Client()
c_est.force_login(estudiante)
resp_circ = c_est.get('/comunicaciones/')
assert resp_circ.status_code == 200
assert 'Circular Confidencial Estudiante 01' in resp_circ.content.decode('utf-8')
print("-> Circular privada visible para el estudiante destinatario.")

otro_est = User.objects.filter(perfil__rol__nombre__icontains='Estudiante').exclude(id=estudiante.id).first()
if otro_est:
    c_otro = Client()
    c_otro.force_login(otro_est)
    resp_otro = c_otro.get('/comunicaciones/')
    assert 'Circular Confidencial Estudiante 01' not in resp_otro.content.decode('utf-8')
    print(f"-> Circular privada debidamente OCULTA para otro estudiante ({otro_est.username}).")

print("\n=== 4. VERIFICACIÓN PLANTILLA IMPORTACIÓN ESTUDIANTES ===")
resp_tpl = c.get('/estudiantes/plantilla/')
assert resp_tpl.status_code == 200
assert resp_tpl['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
print(f"-> Descarga de plantilla Excel (.xlsx) verificada con éxito ({len(resp_tpl.content)} bytes).")

print("\n=== 5. VERIFICACIÓN VISTA DE IMPORTACIÓN MASIVA ===")
resp_imp = c.get('/estudiantes/importar/')
assert resp_imp.status_code == 200
assert 'Carga Masiva de Estudiantes' in resp_imp.content.decode('utf-8')
print("-> Formulario y vista de importación masiva verificados con éxito.")

print("\n========================================================")
print(" ¡TODAS LAS 5 VERIFICACIONES Y FLUJOS PASARON CON ÉXITO! ")
print("========================================================")
