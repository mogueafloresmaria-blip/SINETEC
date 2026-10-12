import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from usuarios.models import PerfilUsuario, Rol, PapeleraReciclaje
from academico.models import Matricula, Ficha

def test_pablo_lorenzo_flow():
    print("=" * 70)
    print("PRUEBA ESPECÍFICA CON PABLO LORENZO Y PROCESO DE DAR DE BAJA")
    print("=" * 70)

    client = Client()

    # Usuario administrativo para login
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin_tmp', 'admin_tmp@edunova.edu.co', 'Admin123*')
    client.force_login(admin_user)

    # 1. Buscar a Pablo Lorenzo
    print("\n--- PASO 1: Buscar a Pablo Lorenzo en la base de datos ---")
    pablo = User.objects.filter(first_name='Pablo', last_name='Lorenzo').first()
    assert pablo is not None, "Error: Pablo Lorenzo debe existir en la base de datos."
    print(f"Pablo Lorenzo encontrado: {pablo.get_full_name()} ({pablo.username})")

    # 2. Consultar su ID real y documento
    print("\n--- PASO 2: Consultar IDs reales de Pablo Lorenzo ---")
    perfil = getattr(pablo, 'perfil', None)
    print(f" - User ID real: {pablo.id}")
    print(f" - PerfilUsuario ID: {perfil.id if perfil else 'N/A'}")
    print(f" - Documento: {perfil.numero_documento if perfil else 'N/A'}")

    # 3. Buscar su matrícula real y relaciones
    print("\n--- PASO 3: Buscar su matrícula real y relaciones de entidad ---")
    matricula = Matricula.objects.filter(aprendiz=pablo).first()
    assert matricula is not None, "Error: Pablo Lorenzo debe tener una matrícula registrada."
    print(f" - Matricula ID real: {matricula.id}")
    print(f" - Ficha asignada: {matricula.ficha.codigo_ficha}")
    print(f" - Grado escolar: {matricula.get_grado_escolar_display()}")
    print(f" - Estado formación actual: {matricula.estado_formacion}")
    print(f" - Relación foránea: Matricula.aprendiz ({matricula.aprendiz_id}) == User.id ({pablo.id}): {matricula.aprendiz_id == pablo.id}")

    # 4. Probar DAR DE BAJA con el identificador de la Matrícula (el caso que antes fallaba)
    print("\n--- PASO 4: Dar de baja al estudiante mediante su Matrícula ID (como envía la tabla) ---")
    # Limpiar papelera previa de Pablo si existe
    PapeleraReciclaje.objects.filter(tipo_objeto='Estudiante', objeto_id=pablo.id).delete()

    url_baja_matricula = f"/estudiantes/{matricula.id}/cambiar-estado/?estado=Desertado"
    response_baja = client.get(url_baja_matricula, follow=True)
    msgs_baja = [m.message for m in get_messages(response_baja.wsgi_request)]

    print(f" - URL invocada: {url_baja_matricula}")
    print(f" - Status HTTP: {response_baja.status_code}")
    print(f" - Mensajes generados: {msgs_baja}")

    # Verificar que NO diga "El aprendiz no tiene una matrícula registrada"
    assert not any("no tiene una matrícula" in m.lower() for m in msgs_baja), "ERROR: Dijo falsamente que no tenía matrícula."
    assert not any("aprendiz" in m.lower() for m in msgs_baja), "ERROR: El término 'aprendiz' apareció en los mensajes."
    assert any("El estudiante Pablo Lorenzo ha sido dado de baja correctamente y enviado a la Papelera de Reciclaje." in m for m in msgs_baja), "ERROR: Mensaje de confirmación de baja no encontrado."

    # 5. Comprobar que el sistema encuentra su matrícula y la envía a Papelera
    print("\n--- PASO 5: Comprobar que la matrícula fue encontrada y enviada a Papelera ---")
    pablo.refresh_from_db()
    matricula.refresh_from_db()
    papelera_item = PapeleraReciclaje.objects.filter(tipo_objeto='Estudiante', objeto_id=pablo.id, restaurado=False).first()

    assert not pablo.is_active, "El usuario debe quedar inactivo"
    assert matricula.estado_formacion in ['Desertado', 'Retirado'], "La matrícula debe quedar en estado de baja"
    assert papelera_item is not None, "El estudiante debe estar registrado en PapeleraReciclaje"
    assert papelera_item.datos_recuperacion.get('tiene_matricula') is True, "Papelera debe registrar que sí tenía matrícula"
    print(f" - Usuario desactivado en BD: {'✅' if not pablo.is_active else '❌'}")
    print(f" - Matrícula actualizada a estado de baja: {'✅' if matricula.estado_formacion == 'Desertado' else '❌'}")
    print(f" - Elemento creado en Papelera con datos de matrícula: {'✅' if papelera_item else '❌'}")
    print(f" - Subtítulo en Papelera: '{papelera_item.subtitulo}'")

    # Restaurar a Pablo Lorenzo para probar también la ruta directa /eliminar/
    print("\n--- PASO 6: Probar también la vista de confirmación /eliminar/ con Pablo Lorenzo ---")
    client.post(f"/papelera/{papelera_item.id}/restaurar/", follow=True)
    pablo.refresh_from_db()
    matricula.refresh_from_db()

    # Probamos con User ID
    resp_get_eliminar = client.get(f"/estudiantes/{pablo.id}/eliminar/")
    assert b"Matr\xc3\xadcula Registrada Confirmada en BD" in resp_get_eliminar.content
    assert b"El estudiante no tiene una matr\xc3\xadcula registrada" not in resp_get_eliminar.content
    print(" - Vista previa con User ID reconoció la matrícula de Pablo: ✅")

    # Probamos con Matricula ID
    resp_get_eliminar_mat = client.get(f"/estudiantes/{matricula.id}/eliminar/")
    assert b"Matr\xc3\xadcula Registrada Confirmada en BD" in resp_get_eliminar_mat.content
    assert b"El estudiante no tiene una matr\xc3\xadcula registrada" not in resp_get_eliminar_mat.content
    print(" - Vista previa con Matricula ID reconoció la matrícula de Pablo: ✅")

    # 7. Probar con un estudiante que REALMENTE NO tiene matrícula
    print("\n--- PASO 7: Probar con un estudiante que verdaderamente NO tiene matrícula ---")
    doc_sin = "8899001122"
    user_sin, _ = User.objects.get_or_create(username=f"alumno_{doc_sin}", defaults={
        'first_name': 'Estudiante', 'last_name': 'SinMatricula', 'email': 'sin@edunova.edu.co'
    })
    perfil_sin, _ = PerfilUsuario.objects.get_or_create(usuario=user_sin, defaults={'numero_documento': doc_sin})
    Matricula.objects.filter(aprendiz=user_sin).delete()

    resp_sin = client.get(f"/estudiantes/{user_sin.id}/cambiar-estado/?estado=Desertado", follow=True)
    msgs_sin = [m.message for m in get_messages(resp_sin.wsgi_request)]
    print(f" - Mensajes generados para estudiante sin matrícula: {msgs_sin}")

    assert any("El estudiante no tiene una matrícula registrada." in m for m in msgs_sin), "ERROR: Debe mostrar 'El estudiante no tiene una matrícula registrada.'"
    assert not any("aprendiz" in m.lower() for m in msgs_sin), "ERROR: No debe aparecer 'aprendiz' en los mensajes."
    print(" - Mensaje exacto 'El estudiante no tiene una matrícula registrada.' verificado: ✅")

    # Limpiar usuario temporal de prueba
    user_sin.delete()
    perfil_sin.delete()

    print("\n" + "=" * 70)
    print("¡TODAS LAS COMPROBACIONES DE PABLO LORENZO Y BAJAS PASARON AL 100%! 🚀")
    print("=" * 70)

if __name__ == '__main__':
    test_pablo_lorenzo_flow()
