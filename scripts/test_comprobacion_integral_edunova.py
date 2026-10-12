import os, sys, django
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

import io
from datetime import date
from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from academico.models import CargaAcademica, Matricula, GuiaClase, ProgramaFormacion
from seguimiento.models import AsistenciaAprendiz
from usuarios.models import PapeleraReciclaje, PerfilUsuario, Rol

def run_all_tests():
    print("=" * 80)
    print("INICIANDO VERIFICACIÓN INTEGRAL DE LOS 6 REQUERIMIENTOS DE EDUNOVA")
    print("=" * 80)

    # Preparar docente y datos de prueba
    docente, _ = User.objects.get_or_create(username='docente', defaults={'first_name': 'Profesor', 'last_name': 'Docente'})
    docente.set_password('edunova123')
    docente.is_active = True
    docente.save()

    rol_doc, _ = Rol.objects.get_or_create(nombre='Docente', defaults={'descripcion': 'Docente'})
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=docente, defaults={'rol': rol_doc, 'esta_activo': True})
    perfil.rol = rol_doc
    perfil.esta_activo = True
    perfil.save()

    # Carga académica para el docente
    carga = CargaAcademica.objects.filter(profesor=docente).first()
    if not carga:
        prog = ProgramaFormacion.objects.first()
        if not prog:
            prog = ProgramaFormacion.objects.create(codigo_programa='MAT10', denominacion='Matemáticas Avanzadas', version=1)
        carga = CargaAcademica.objects.create(
            profesor=docente,
            grado='10',
            seccion='A',
            programa=prog,
            ano_lectivo=2026,
            horas_semanales=4
        )

    # Obtener o asignar matrícula real para la prueba
    from academico.models import Ficha
    ficha_obj = Ficha.objects.first()
    mat = Matricula.objects.filter(estado_formacion='En Formacion').first()
    if not mat:
        est_u, _ = User.objects.get_or_create(username='est_prueba_asist', defaults={'first_name': 'Carlos', 'last_name': 'Gomez'})
        mat = Matricula.objects.create(
            aprendiz=est_u,
            ficha=ficha_obj,
            grado_escolar=str(carga.grado),
            seccion=carga.seccion,
            estado_formacion='En Formacion'
        )
    else:
        mat.grado_escolar = str(carga.grado)
        mat.seccion = carga.seccion
        mat.estado_formacion = 'En Formacion'
        mat.save(update_fields=['grado_escolar', 'seccion', 'estado_formacion'])

    client = Client()
    client.force_login(docente)

    # =========================================================================
    # PRUEBA 1: ASISTENCIA DOCENTE
    # =========================================================================
    print("\n--- PRUEBA 1: ASISTENCIA DOCENTE ---")
    fecha_hoy = date.today().isoformat()
    resp_asist_get = client.get(f'/asistencia/?carga={carga.id}&fecha={fecha_hoy}')
    assert resp_asist_get.status_code == 200, f"Error GET asistencia: {resp_asist_get.status_code}"
    body_asist = resp_asist_get.content.decode('utf-8')
    assert mat.aprendiz.username in body_asist or (mat.aprendiz.first_name and mat.aprendiz.first_name in body_asist), "El estudiante no aparece en la lista de asistencia"
    print("  [OK] Paso 1: Módulo de Asistencia accesible y estudiante listado.")

    # Guardar asistencia como Presente (P)
    post_data_p = {
        'action': 'guardar_asistencia',
        'carga_id': str(carga.id),
        'fecha_asistencia': fecha_hoy,
        'periodo': 'Periodo 1',
        f'asistencia_{mat.id}': 'P',
        f'obs_{mat.id}': 'Llegó a tiempo y participó activamente',
    }
    resp_asist_post = client.post('/asistencia/', post_data_p, follow=True)
    assert resp_asist_post.status_code == 200, f"Error POST asistencia: {resp_asist_post.status_code}"
    
    # Comprobar en base de datos
    registro_asist = AsistenciaAprendiz.objects.filter(matricula=mat, fecha=date.today()).first()
    assert registro_asist is not None, "La asistencia NO se guardó en la base de datos!"
    assert registro_asist.estado == 'P', f"Estado incorrecto: {registro_asist.estado} != P"
    assert 'participó activamente' in registro_asist.observaciones, "La observación no se guardó"
    print("  [OK] Paso 2: Asistencia 'P' guardada en DB con observación.")

    # Recargar página y comprobar persistencia
    resp_reload = client.get(f'/asistencia/?carga={carga.id}&fecha={fecha_hoy}')
    assert resp_reload.status_code == 200, "Error al recargar página de asistencia"
    reload_body = resp_reload.content.decode('utf-8')
    assert f'id="asist_p_{mat.id}" value="P" checked' in reload_body or f'checked onchange="actualizarKpisEnVivo();"' in reload_body, "La marcación no permanece activa al recargar"
    print("  [OK] Paso 3: Recarga exitosa y estado 'P' persistido visualmente.")

    # Modificar a Ausente (A) para validar actualización sin duplicados
    post_data_a = {
        'action': 'guardar_asistencia',
        'carga_id': str(carga.id),
        'fecha_asistencia': fecha_hoy,
        'periodo': 'Periodo 1',
        f'asistencia_{mat.id}': 'A',
        f'obs_{mat.id}': 'Inasistencia no justificada',
    }
    resp_asist_post2 = client.post('/asistencia/', post_data_a, follow=True)
    assert resp_asist_post2.status_code == 200
    registro_asist2 = AsistenciaAprendiz.objects.filter(matricula=mat, fecha=date.today()).first()
    assert registro_asist2.estado == 'A', f"Actualización fallida: {registro_asist2.estado} != A"
    # Verificar que no duplicó el registro
    total_asists = AsistenciaAprendiz.objects.filter(matricula=mat, fecha=date.today()).count()
    assert total_asists == 1, f"Se duplicó el registro de asistencia: total {total_asists}"
    print("  [OK] Paso 4: Actualización a 'A' exitosa y sin duplicados en DB.")
    print(">>> PRUEBA 1 SUPERADA EXITOSAMENTE! <<<\n")

    # =========================================================================
    # PRUEBA 2: 📘 GUÍA (PUBLICAR -> LISTAR -> ELIMINAR -> PAPELERA -> RECUPERAR)
    # =========================================================================
    print("--- PRUEBA 2: 📘 GUÍA ---")
    fake_file_guia = SimpleUploadedFile("guia_algebra.pdf", b"Contenido de guia", content_type="application/pdf")
    resp_guia = client.post('/docente/', {
        'action': 'publicar_guia',
        'titulo': 'Guía Oficial N° 1 de Álgebra Lineal',
        'carga_id': str(carga.id),
        'instrucciones': 'Resolver ejercicios 1 al 10',
        'archivo': fake_file_guia
    }, follow=True)
    assert resp_guia.status_code == 200

    # Comprobar en BD
    guia_obj = GuiaClase.objects.filter(titulo='Guía Oficial N° 1 de Álgebra Lineal').first()
    assert guia_obj is not None, "La guía no fue creada en la BD!"
    assert guia_obj.tipo_documento == 'GUIA', f"Tipo incorrecto: {guia_obj.tipo_documento} != GUIA"
    assert guia_obj.estado == 'ACTIVO', "El estado inicial debe ser ACTIVO"
    print(f"  [OK] 1. Guía creada con tipo_documento='GUIA' (ID #{guia_obj.id})")

    # Ver en listado de guías
    resp_list_guias = client.get('/docente/?subpanel=documentos&tab=guias')
    assert resp_list_guias.status_code == 200
    assert 'Guía Oficial N° 1 de Álgebra Lineal' in resp_list_guias.content.decode('utf-8'), "La guía no aparece en el listado de Guías"
    print("  [OK] 2. Guía visible en el listado de Guías.")

    # Eliminar -> Enviar a papelera
    resp_del_guia = client.post('/docente/', {
        'action': 'eliminar_documento',
        'documento_id': str(guia_obj.id)
    }, follow=True)
    assert resp_del_guia.status_code == 200

    guia_obj.refresh_from_db()
    assert guia_obj.estado == 'PAPELERA', "El estado de la guía no cambió a PAPELERA"
    item_pap_guia = PapeleraReciclaje.objects.filter(tipo_objeto='GuiaClase', objeto_id=guia_obj.id, restaurado=False).first()
    assert item_pap_guia is not None, "La guía no fue registrada en PapeleraReciclaje!"
    assert 'Documentos → Guías' in item_pap_guia.modulo_origen, f"Módulo de origen incorrecto: {item_pap_guia.modulo_origen}"
    print(f"  [OK] 3. Guía trasladada a Papelera con módulo de origen '{item_pap_guia.modulo_origen}'.")

    # Recuperar desde la papelera
    resp_recup_guia = client.post('/docente/', {
        'action': 'restaurar_papelera',
        'papelera_id': str(item_pap_guia.id)
    }, follow=True)
    assert resp_recup_guia.status_code == 200
    guia_obj.refresh_from_db()
    assert guia_obj.estado == 'ACTIVO', "La guía no fue restaurada a ACTIVO"

    # Verificar que regresó al listado de Guías
    resp_check_guia = client.get('/docente/?subpanel=documentos&tab=guias')
    assert 'Guía Oficial N° 1 de Álgebra Lineal' in resp_check_guia.content.decode('utf-8'), "La guía no regresó al listado de Guías"
    print("  [OK] 4. Guía recuperada exitosamente y visible de nuevo en Documentos → Guías.")
    print(">>> PRUEBA 2 SUPERADA EXITOSAMENTE! <<<\n")

    # =========================================================================
    # PRUEBA 3: 📚 MATERIAL PEDAGÓGICO
    # =========================================================================
    print("--- PRUEBA 3: 📚 MATERIAL PEDAGÓGICO ---")
    fake_file_ped = SimpleUploadedFile("modulo_didactico.pdf", b"Contenido didactico", content_type="application/pdf")
    resp_ped = client.post('/docente/', {
        'action': 'publicar_material_pedagogico',
        'titulo': 'Módulo Didáctico de Trigonometría',
        'carga_id': str(carga.id),
        'instrucciones': 'Lectura y comprensión del capítulo 3',
        'archivo': fake_file_ped
    }, follow=True)
    assert resp_ped.status_code == 200

    ped_obj = GuiaClase.objects.filter(titulo='Módulo Didáctico de Trigonometría').first()
    assert ped_obj is not None, "El material pedagógico no fue creado!"
    assert ped_obj.tipo_documento == 'MATERIAL_PEDAGOGICO', f"Tipo incorrecto: {ped_obj.tipo_documento} != MATERIAL_PEDAGOGICO"
    assert ped_obj.estado == 'ACTIVO'
    print(f"  [OK] 1. Material pedagógico creado con tipo='MATERIAL_PEDAGOGICO' (ID #{ped_obj.id})")

    # Ver en listado de material pedagógico
    resp_list_ped = client.get('/docente/?subpanel=documentos&tab=pedagogico')
    assert 'Módulo Didáctico de Trigonometría' in resp_list_ped.content.decode('utf-8')
    print("  [OK] 2. Material pedagógico visible en pestaña correspondiente.")

    # Eliminar
    client.post('/docente/', {'action': 'eliminar_documento', 'documento_id': str(ped_obj.id)}, follow=True)
    ped_obj.refresh_from_db()
    assert ped_obj.estado == 'PAPELERA'
    item_pap_ped = PapeleraReciclaje.objects.filter(tipo_objeto='GuiaClase', objeto_id=ped_obj.id, restaurado=False).first()
    assert 'Material pedagógico' in item_pap_ped.modulo_origen
    print(f"  [OK] 3. Material pedagógico en papelera con origen '{item_pap_ped.modulo_origen}'.")

    # Recuperar
    client.post('/docente/', {'action': 'restaurar_papelera', 'papelera_id': str(item_pap_ped.id)}, follow=True)
    ped_obj.refresh_from_db()
    assert ped_obj.estado == 'ACTIVO'
    resp_check_ped = client.get('/docente/?subpanel=documentos&tab=pedagogico')
    assert 'Módulo Didáctico de Trigonometría' in resp_check_ped.content.decode('utf-8')
    print("  [OK] 4. Material pedagógico recuperado y retornado a su listado original.")
    print(">>> PRUEBA 3 SUPERADA EXITOSAMENTE! <<<\n")

    # =========================================================================
    # PRUEBA 4: 📎 MATERIAL DE APOYO
    # =========================================================================
    print("--- PRUEBA 4: 📎 MATERIAL DE APOYO ---")
    fake_file_apo = SimpleUploadedFile("tablas_apoyo.pdf", b"Tablas de apoyo", content_type="application/pdf")
    resp_apo = client.post('/docente/', {
        'action': 'publicar_material_apoyo',
        'titulo': 'Formulario y Tablas de Apoyo Matemático',
        'carga_id': str(carga.id),
        'instrucciones': 'Documento de consulta rápida para evaluaciones',
        'archivo': fake_file_apo
    }, follow=True)
    assert resp_apo.status_code == 200

    apo_obj = GuiaClase.objects.filter(titulo='Formulario y Tablas de Apoyo Matemático').first()
    assert apo_obj is not None, "El material de apoyo no fue creado!"
    assert apo_obj.tipo_documento == 'MATERIAL_APOYO', f"Tipo incorrecto: {apo_obj.tipo_documento} != MATERIAL_APOYO"
    assert apo_obj.estado == 'ACTIVO'
    print(f"  [OK] 1. Material de apoyo creado con tipo='MATERIAL_APOYO' (ID #{apo_obj.id})")

    # Ver en listado de material de apoyo
    resp_list_apo = client.get('/docente/?subpanel=documentos&tab=apoyo')
    assert 'Formulario y Tablas de Apoyo Matemático' in resp_list_apo.content.decode('utf-8')
    print("  [OK] 2. Material de apoyo visible en pestaña correspondiente.")

    # Eliminar
    client.post('/docente/', {'action': 'eliminar_documento', 'documento_id': str(apo_obj.id)}, follow=True)
    apo_obj.refresh_from_db()
    assert apo_obj.estado == 'PAPELERA'
    item_pap_apo = PapeleraReciclaje.objects.filter(tipo_objeto='GuiaClase', objeto_id=apo_obj.id, restaurado=False).first()
    assert 'Material de apoyo' in item_pap_apo.modulo_origen
    print(f"  [OK] 3. Material de apoyo en papelera con origen '{item_pap_apo.modulo_origen}'.")

    # Recuperar
    client.post('/docente/', {'action': 'restaurar_papelera', 'papelera_id': str(item_pap_apo.id)}, follow=True)
    apo_obj.refresh_from_db()
    assert apo_obj.estado == 'ACTIVO'
    resp_check_apo = client.get('/docente/?subpanel=documentos&tab=apoyo')
    assert 'Formulario y Tablas de Apoyo Matemático' in resp_check_apo.content.decode('utf-8')
    print("  [OK] 4. Material de apoyo recuperado y retornado a su listado original.")
    print(">>> PRUEBA 4 SUPERADA EXITOSAMENTE! <<<\n")

    # =========================================================================
    # PRUEBA 5: CERRAR SESIÓN Y PREVENCIÓN DE CACHÉ
    # =========================================================================
    print("--- PRUEBA 5: CERRAR SESIÓN Y PREVENCIÓN DE CACHÉ ---")
    # Verificar headers de control de caché en vista del docente
    resp_cache = client.get('/docente/')
    cache_ctrl = resp_cache.headers.get('Cache-Control', '')
    assert 'no-cache' in cache_ctrl or 'max-age=0' in cache_ctrl, f"Falta header never_cache: {cache_ctrl}"
    print(f"  [OK] 1. Headers de caché validados: {cache_ctrl}")

    # Verificar que el botón de Cerrar sesión existe en el HTML
    body_doc = resp_cache.content.decode('utf-8')
    assert 'Cerrar sesión' in body_doc or 'Cerrar Sesión' in body_doc, "Falta botón Cerrar sesión en el panel del docente"
    assert "action=\"/accounts/logout/\"" in body_doc or "action=\"/logout/\"" in body_doc, "El formulario de logout no apunta a la ruta de logout de Django"
    print("  [OK] 2. Botón de 'Cerrar sesión' presente en la interfaz.")

    # Ejecutar logout real
    resp_logout = client.post('/logout/', follow=False)
    assert resp_logout.status_code in [302, 200], f"Logout inesperado: {resp_logout.status_code}"
    # Verificar que el usuario ya no está autenticado
    resp_post_logout = client.get('/asistencia/', follow=False)
    assert resp_post_logout.status_code == 302, f"Debe redirigir al login al no estar autenticado, obtuvo: {resp_post_logout.status_code}"
    assert '/login/' in resp_post_logout['Location'] or '/accounts/login/' in resp_post_logout['Location']
    print("  [OK] 3. Cierre de sesión real confirmado: intento de acceso redirige a login.")
    print(">>> PRUEBA 5 SUPERADA EXITOSAMENTE! <<<\n")

    # =========================================================================
    # PRUEBA 6: PAPELERA DE RECICLAJE (CAMPOS OBLIGATORIOS)
    # =========================================================================
    print("--- PRUEBA 6: PAPELERA DE RECICLAJE ---")
    # Reautenticar para verificar la interfaz de papelera
    client.force_login(docente)
    
    # Crear un elemento para enviar a papelera y verificar visualización completa
    guia_test_pap = GuiaClase.objects.create(
        profesor=docente,
        carga_academica=carga,
        tipo_documento='GUIA',
        titulo='Guía para Auditoría de Papelera',
        estado='ACTIVO'
    )
    client.post('/docente/', {'action': 'eliminar_documento', 'documento_id': str(guia_test_pap.id)}, follow=True)

    resp_pap = client.get('/docente/?subpanel=papelera')
    assert resp_pap.status_code == 200
    pap_html = resp_pap.content.decode('utf-8')

    # Verificar presencia de los 6 requisitos:
    assert 'NOMBRE' in pap_html, "Falta columna Nombre en tabla de papelera"
    assert 'TIPO' in pap_html, "Falta columna Tipo en tabla de papelera"
    assert 'MÓDULO DE ORIGEN' in pap_html, "Falta columna Módulo de origen en tabla de papelera"
    assert 'FECHA DE ELIMINACIÓN' in pap_html, "Falta columna Fecha de eliminación en tabla de papelera"
    assert 'USUARIO QUE ELIMINÓ' in pap_html, "Falta columna Usuario que eliminó en tabla de papelera"
    assert 'Recuperar' in pap_html, "Falta botón Recuperar en tabla de papelera"
    assert 'Guía para Auditoría de Papelera' in pap_html, "El elemento en papelera no se muestra en el HTML"
    assert 'Documentos → Guías' in pap_html, "El módulo de origen no se muestra en el HTML"

    print("  [OK] 1. Columna 'NOMBRE' presente.")
    print("  [OK] 2. Columna 'TIPO' presente.")
    print("  [OK] 3. Columna 'MÓDULO DE ORIGEN' presente con 'Documentos → Guías'.")
    print("  [OK] 4. Columna 'FECHA DE ELIMINACIÓN' presente.")
    print("  [OK] 5. Columna 'USUARIO QUE ELIMINÓ' presente.")
    print("  [OK] 6. Botón '♻️ Recuperar' presente.")
    print(">>> PRUEBA 6 SUPERADA EXITOSAMENTE! <<<\n")

    # Limpieza de prueba
    GuiaClase.objects.filter(titulo__icontains='Guía Oficial N° 1').delete()
    GuiaClase.objects.filter(titulo__icontains='Módulo Didáctico').delete()
    GuiaClase.objects.filter(titulo__icontains='Formulario y Tablas').delete()
    GuiaClase.objects.filter(titulo__icontains='Guía para Auditoría').delete()

    print("=" * 80)
    print("TODAS LAS 6 PRUEBAS OBLIGATORIAS PASARON AL 100% CON ÉXITO")
    print("=" * 80)

if __name__ == '__main__':
    run_all_tests()
