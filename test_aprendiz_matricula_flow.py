import os
import sys
import django

sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from academico.models import Ficha, Matricula, ProgramaFormacion
from instituciones.models import InstitucionEducativa
from usuarios.models import PerfilUsuario, Rol, PapeleraReciclaje

def run_tests():
    print("=" * 70)
    print("EJECUTANDO PRUEBAS OBLIGATORIAS: APRENDICES Y MATRÍCULAS EDUNOVA")
    print("=" * 70)

    client = Client()

    # 0. Preparación de usuario administrador/secretaría para autenticación
    admin_user, _ = User.objects.get_or_create(username='admin_test_flow', defaults={
        'first_name': 'Admin', 'last_name': 'Test', 'email': 'admin_flow@edunova.edu.co', 'is_staff': True, 'is_superuser': True
    })
    admin_user.set_password('AdminPass123*')
    admin_user.save()
    rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador', defaults={'descripcion': 'Admin'})
    perfil_admin, _ = PerfilUsuario.objects.get_or_create(usuario=admin_user, defaults={'rol': rol_admin, 'numero_documento': '99999999'})
    perfil_admin.rol = rol_admin
    perfil_admin.save()

    ficha_valida = Ficha.objects.filter(estado='En Ejecucion').first() or Ficha.objects.first()
    if not ficha_valida:
        institucion, _ = InstitucionEducativa.objects.get_or_create(nombre='Colegio Central Edunova', defaults={'codigo_dane': '111111'})
        programa, _ = ProgramaFormacion.objects.get_or_create(codigo_programa='PRG01', defaults={'denominacion': 'Técnico en Sistemas'})
        ficha_valida = Ficha.objects.create(codigo_ficha='10-A-2026', programa=programa, institucion=institucion, estado='En Ejecucion')

    client.force_login(admin_user)

    # -------------------------------------------------------------
    # PRUEBA 1: Registro correcto
    # -------------------------------------------------------------
    print("\n>>> PRUEBA 1: Registro correcto de aprendiz con matrícula válida...")
    doc_p1 = "1099887701"
    def limpiar_estudiante(doc):
        u = User.objects.filter(username=f'alumno_{doc}').first()
        if u:
            Matricula.objects.filter(aprendiz=u).delete()
            PapeleraReciclaje.objects.filter(objeto_id=u.id).delete()
            PerfilUsuario.objects.filter(usuario=u).delete()
            u.delete()
        PerfilUsuario.objects.filter(numero_documento=doc).delete()

    limpiar_estudiante(doc_p1)

    post_data_p1 = {
        'nombres': 'Carlos Andrés',
        'apellidos': 'Gómez Pérez',
        'tipo_documento': 'TI',
        'documento': doc_p1,
        'correo': 'carlos.gomez@edunova.edu.co',
        'telefono': '3001234567',
        'genero': 'Masculino',
        'ficha_id': str(ficha_valida.id),
        'acudiente_nombre': 'Marta Pérez',
        'acudiente_telefono': '3109876543'
    }

    response_p1 = client.post('/estudiantes/registrar/', post_data_p1, follow=True)
    msgs_p1 = [m.message for m in get_messages(response_p1.wsgi_request)]

    # Comprobaciones directas en Base de Datos:
    user_p1 = User.objects.filter(email='carlos.gomez@edunova.edu.co').first()
    aprendiz_existe_bd = user_p1 is not None
    perfil_p1 = PerfilUsuario.objects.filter(numero_documento=doc_p1).first() if user_p1 else None
    matricula_p1 = Matricula.objects.filter(aprendiz=user_p1, ficha=ficha_valida).first() if user_p1 else None
    matricula_existe_bd = matricula_p1 is not None
    relacion_existe_bd = (matricula_p1.aprendiz_id == user_p1.id and matricula_p1.ficha_id == ficha_valida.id) if matricula_p1 else False

    print(f" - Aprendiz existe en BD: {'✅' if aprendiz_existe_bd else '❌'} (ID: {user_p1.id if user_p1 else 'N/A'})")
    print(f" - Matrícula existe en BD: {'✅' if matricula_existe_bd else '❌'} (ID: {matricula_p1.id if matricula_p1 else 'N/A'})")
    print(f" - Relación Aprendiz-Matrícula existe: {'✅' if relacion_existe_bd else '❌'}")
    print(f" - Mensajes generados: {msgs_p1}")

    assert aprendiz_existe_bd, "Fallo: Aprendiz no fue guardado en BD."
    assert matricula_existe_bd, "Fallo: Matrícula no fue guardada en BD."
    assert relacion_existe_bd, "Fallo: Relación Aprendiz-Matrícula no coincide."
    assert any("Aprendiz y matrícula registrados correctamente" in m for m in msgs_p1), "Fallo: Mensaje de éxito esperado no fue emitido."
    print(">>> PRUEBA 1 COMPLETADA CON ÉXITO ✅")

    # -------------------------------------------------------------
    # PRUEBA 2: Simulación de error en matrícula
    # -------------------------------------------------------------
    print("\n>>> PRUEBA 2: Aprendiz creado pero matrícula NO guardada (ficha inválida/error)...")
    doc_p2 = "1099887702"
    limpiar_estudiante(doc_p2)

    post_data_p2 = {
        'nombres': 'Laura Sofía',
        'apellidos': 'Torres Ruiz',
        'tipo_documento': 'TI',
        'documento': doc_p2,
        'correo': 'laura.torres@edunova.edu.co',
        'telefono': '3005556677',
        'genero': 'Femenino',
        'ficha_id': '999999',  # Ficha inexistente que provoca fallo controlado en la matrícula
    }

    response_p2 = client.post('/estudiantes/registrar/', post_data_p2, follow=True)
    msgs_p2 = [m.message for m in get_messages(response_p2.wsgi_request)]

    user_p2 = User.objects.filter(email='laura.torres@edunova.edu.co').first()
    aprendiz_p2_existe = user_p2 is not None
    matricula_p2_existe = Matricula.objects.filter(aprendiz=user_p2).exists() if user_p2 else False

    print(f" - Aprendiz creado en BD: {'✅' if aprendiz_p2_existe else '❌'} (ID: {user_p2.id if user_p2 else 'N/A'})")
    print(f" - Matrícula NO existe en BD: {'✅ Correcto (No se inventó matrícula)' if not matricula_p2_existe else '❌ Error'}")
    print(f" - Mensajes generados: {msgs_p2}")

    # No debe decir que la matrícula fue registrada correctamente:
    assert not any("matriculado correctamente" in m for m in msgs_p2), "Fallo: Dijo falsamente que la matrícula fue registrada."
    assert any("El aprendiz fue registrado, pero la matrícula no pudo registrarse" in m for m in msgs_p2), "Fallo: Mensaje de advertencia esperado no fue emitido."
    print(">>> PRUEBA 2 COMPLETADA CON ÉXITO ✅")

    # -------------------------------------------------------------
    # PRUEBA 3: Eliminación de aprendiz con matrícula existente
    # -------------------------------------------------------------
    print("\n>>> PRUEBA 3: Eliminación de aprendiz CON matrícula hacia Papelera...")
    # Verificamos que user_p1 tiene matrícula
    assert Matricula.objects.filter(aprendiz=user_p1).exists(), "user_p1 debe tener matrícula para esta prueba"

    response_get_p3 = client.get(f'/estudiantes/{user_p1.id}/eliminar/')
    print(f" - Status GET: {response_get_p3.status_code}")
    assert b"Matr\xc3\xadcula Registrada Confirmada en BD" in response_get_p3.content, "La vista previa debe mostrar la matrícula confirmada en BD"
    assert b"Este aprendiz no tiene una matr\xc3\xadcula registrada" not in response_get_p3.content, "No debe decir que no tiene matrícula"
    print(" - Vista previa GET detectó matrícula activa y mostró bloque de confirmación: ✅")

    # POST para eliminar y enviar a papelera
    response_p3 = client.post(f'/estudiantes/{user_p1.id}/eliminar/', follow=True)
    msgs_p3 = [m.message for m in get_messages(response_p3.wsgi_request)]

    user_p1.refresh_from_db()
    mat_p1_actualizada = Matricula.objects.filter(aprendiz=user_p1).first()
    papelera_p1 = PapeleraReciclaje.objects.filter(tipo_objeto='Estudiante', objeto_id=user_p1.id, restaurado=False).first()

    print(f" - Usuario desactivado: {'✅' if not user_p1.is_active else '❌'}")
    print(f" - Matrícula pausada a 'Retirado': {'✅' if mat_p1_actualizada.estado_formacion == 'Retirado' else '❌'}")
    print(f" - Elemento creado en Papelera con datos de matrícula: {'✅' if (papelera_p1 and papelera_p1.datos_recuperacion.get('tiene_matricula')) else '❌'}")
    print(f" - Mensajes generados: {msgs_p3}")

    assert papelera_p1 is not None, "Debe existir registro en PapeleraReciclaje"
    assert papelera_p1.datos_recuperacion.get('tiene_matricula') is True, "Papelera debe contener tiene_matricula=True"
    print(">>> PRUEBA 3 COMPLETADA CON ÉXITO ✅")

    # -------------------------------------------------------------
    # PRUEBA 4: Aprendiz sin matrícula registrada
    # -------------------------------------------------------------
    print("\n>>> PRUEBA 4: Gestión/Eliminación de aprendiz SIN matrícula registrada...")
    # user_p2 no tiene matrícula
    assert not Matricula.objects.filter(aprendiz=user_p2).exists(), "user_p2 no debe tener matrícula"

    # GET: Debe advertir "Este aprendiz no tiene una matrícula registrada."
    response_get_p4 = client.get(f'/estudiantes/{user_p2.id}/eliminar/')
    msgs_get_p4 = [m.message for m in get_messages(response_get_p4.wsgi_request)]
    print(f" - Mensajes en GET: {msgs_get_p4}")
    assert any("Este aprendiz no tiene una matrícula registrada" in m for m in msgs_get_p4), "Fallo: GET debe advertir que no tiene matrícula"
    assert b"Este aprendiz no tiene una matr\xc3\xadcula registrada" in response_get_p4.content, "Template debe contener el texto de alerta"
    assert b"Matr\xc3\xadcula Registrada Confirmada en BD" not in response_get_p4.content, "Template no debe mostrar matrícula confirmada"
    print(" - Vista previa detectó ausencia de matrícula y mostró mensaje exacto: ✅")

    # POST: Eliminación de usuario sin matrícula hacia papelera
    response_p4 = client.post(f'/estudiantes/{user_p2.id}/eliminar/', follow=True)
    msgs_p4 = [m.message for m in get_messages(response_p4.wsgi_request)]
    print(f" - Mensajes en POST: {msgs_p4}")

    papelera_p2 = PapeleraReciclaje.objects.filter(tipo_objeto='Estudiante', objeto_id=user_p2.id, restaurado=False).first()
    assert papelera_p2 is not None, "El usuario sin matrícula debe quedar en papelera"
    assert papelera_p2.datos_recuperacion.get('tiene_matricula') is False, "Papelera debe indicar tiene_matricula=False sin inventar matrículas"
    assert "Sin matrícula registrada" in papelera_p2.subtitulo, "Subtítulo en papelera debe indicar sin matrícula"
    assert any("Este aprendiz no tiene una matrícula registrada" in m for m in msgs_p4), "Fallo: Mensaje de confirmación POST debe avisar que no tenía matrícula"
    print(" - Papelera resguardó al aprendiz sin inventar matrícula inexistente: ✅")
    print(">>> PRUEBA 4 COMPLETADA CON ÉXITO ✅")

    # -------------------------------------------------------------
    # PRUEBA ADICIONAL: Restauración desde Papelera
    # -------------------------------------------------------------
    print("\n>>> PRUEBA 5 (Papelera y Restauración):")
    # Restaurar user_p1 (con matrícula)
    resp_res_p1 = client.post(f'/papelera/{papelera_p1.id}/restaurar/', follow=True)
    user_p1.refresh_from_db()
    mat_p1_res = Matricula.objects.filter(aprendiz=user_p1).first()
    assert user_p1.is_active is True, "Usuario debe quedar activo"
    assert mat_p1_res.estado_formacion == 'En Formacion', "Matrícula debe restaurarse a 'En Formacion'"
    print(" - Restauración de aprendiz CON matrícula exitosa (estado reactivado a 'En Formación'): ✅")

    # Restaurar user_p2 (sin matrícula)
    resp_res_p2 = client.post(f'/papelera/{papelera_p2.id}/restaurar/', follow=True)
    user_p2.refresh_from_db()
    assert user_p2.is_active is True, "Usuario debe quedar activo"
    assert not Matricula.objects.filter(aprendiz=user_p2).exists(), "No debe inventar matrícula para aprendiz que no la tenía"
    print(" - Restauración de aprendiz SIN matrícula exitosa (continúa sin matrícula, sin inventar registros): ✅")

    print("\n" + "=" * 70)
    print("¡TODAS LAS PRUEBAS OBLIGATORIAS (1, 2, 3 Y 4) PASARON SATISFACTORIAMENTE! 🚀")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
