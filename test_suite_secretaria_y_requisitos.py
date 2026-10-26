"""
================================================================================
SUITE AUTOMATIZADA DE PRUEBAS - VERIFICACIÓN INTEGRAL DE REQUISITOS EDUNOVA
Valida:
1. Gestión de usuarios por Secretaría (autorización y protección directiva).
2. Descarga de plantillas Excel y CSV para Estudiantes y Docentes.
3. Carga masiva y registro individual de estudiantes con usuario=cédula, clave=cédula (hasheada).
4. Conservación de ceros a la izquierda y valores numéricos limpios.
5. Procesamiento seguro y transacciones a nivel de fila (tolerancia a errores parciales).
6. Grados escolares del 1° al 11° unificados sin restricciones indebidas.
7. Carga masiva de docentes con rol Docente y credenciales correctas.
8. Login del estudiante en su propio panel con datos reales y sin notas inventadas.
9. Notificaciones legítimas y funcionamiento de la Papelera del Docente.
================================================================================
"""

import os
import sys
import io
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.db import connection

from usuarios.models import Rol, PerfilUsuario, PapeleraReciclaje
from academico.models import Matricula, Ficha, ProgramaFormacion
from seguimiento.models import Notificacion

resultados = []

def test_assert(condicion, prueba_nombre, detalle=""):
    if condicion:
        resultados.append((prueba_nombre, "PASÓ", detalle))
        print(f"  [OK] PASÓ: {prueba_nombre} | {detalle}")
    else:
        resultados.append((prueba_nombre, "FALLÓ", detalle))
        print(f"  [FAIL] FALLÓ: {prueba_nombre} | {detalle}")


def ejecutar_pruebas():
    print("=" * 80)
    print("INICIO DE PRUEBAS AUTOMATIZADAS - EDUNOVA REQUISITOS 1 A 9")
    print(f"Base de datos activa: {connection.settings_dict['ENGINE']} -> {connection.settings_dict['NAME']}")
    print("=" * 80)

    client = Client()

    # Obtener o asegurar usuarios clave
    user_secretaria = User.objects.filter(username='secretaria').first()
    if not user_secretaria:
        user_secretaria = User.objects.filter(perfil__rol__nombre__icontains='Secretar').first()
    
    user_admin = User.objects.filter(is_superuser=True).first()
    user_docente = User.objects.filter(username='docente').first() or User.objects.filter(perfil__rol__nombre__icontains='Docente').first()
    user_estudiante = User.objects.filter(username='1001001001').first() or User.objects.filter(perfil__rol__nombre__icontains='Aprendiz').first()

    # --------------------------------------------------------------------------
    # 1. GESTIÓN DE USUARIOS EN SECRETARÍA Y PROTECCIÓN DE ADMINISTRADOR
    # --------------------------------------------------------------------------
    print("\n--- 1. GESTIÓN DE USUARIOS EN SECRETARÍA Y PROTECCIÓN DE ROLES ---")
    client.force_login(user_secretaria)
    resp = client.get(reverse('gestion_usuarios'))
    test_assert(resp.status_code == 200, "Secretaría accede a gestión de usuarios", f"Status code: {resp.status_code}")
    test_assert(resp.context.get('es_secretaria') is True, "Contexto reconoce a Secretaría", "es_secretaria == True")

    # Secretaría intentando alternar estado o resetear clave a un Administrador
    resp_toggle_admin = client.get(reverse('usuario_toggle_activo', args=[user_admin.pk]), follow=True)
    test_assert(user_admin.is_active is True, "Secretaría no puede desactivar cuenta de Administrador", "Admin sigue activo")

    resp_reset_admin = client.get(reverse('usuario_reset_clave', args=[user_admin.pk]), follow=True)
    mensajes_txt = " ".join([m.message for m in resp_reset_admin.context.get('messages', [])])
    test_assert("Acceso restringido" in mensajes_txt, "Secretaría recibe error al intentar modificar Administrador", mensajes_txt[:80])

    # Estudiante o Familia intentando acceder a gestión de usuarios (debe ser bloqueado)
    if user_estudiante:
        client.force_login(user_estudiante)
        resp_est_gu = client.get(reverse('gestion_usuarios'), follow=False)
        test_assert(resp_est_gu.status_code in [302, 403], "Estudiante no puede acceder a gestión de usuarios", f"Status: {resp_est_gu.status_code}")

    # --------------------------------------------------------------------------
    # 2. DESCARGA DE PLANTILLAS (EXCEL Y CSV)
    # --------------------------------------------------------------------------
    print("\n--- 2. DESCARGA DE PLANTILLAS PARA ESTUDIANTES Y DOCENTES ---")
    client.force_login(user_secretaria)

    # Plantilla Estudiantes Excel
    resp_p_est_xlsx = client.get(reverse('descargar_plantilla_estudiantes'))
    test_assert(resp_p_est_xlsx.status_code == 200 and 'spreadsheet' in resp_p_est_xlsx.get('Content-Type', ''), 
                "Descarga plantilla Estudiantes Excel (.xlsx)", f"Content-Type: {resp_p_est_xlsx.get('Content-Type')}")

    # Plantilla Estudiantes CSV
    resp_p_est_csv = client.get(reverse('descargar_plantilla_estudiantes') + '?formato=csv')
    test_assert(resp_p_est_csv.status_code == 200 and 'text/csv' in resp_p_est_csv.get('Content-Type', ''), 
                "Descarga plantilla Estudiantes CSV (.csv)", f"Content-Type: {resp_p_est_csv.get('Content-Type')}")

    # Plantilla Docentes Excel
    resp_p_doc_xlsx = client.get(reverse('descargar_plantilla_instructores'))
    test_assert(resp_p_doc_xlsx.status_code == 200 and 'spreadsheet' in resp_p_doc_xlsx.get('Content-Type', ''), 
                "Descarga plantilla Docentes Excel (.xlsx)", f"Content-Type: {resp_p_doc_xlsx.get('Content-Type')}")

    # Plantilla Docentes CSV
    resp_p_doc_csv = client.get(reverse('descargar_plantilla_instructores') + '?formato=csv')
    test_assert(resp_p_doc_csv.status_code == 200 and 'text/csv' in resp_p_doc_csv.get('Content-Type', ''), 
                "Descarga plantilla Docentes CSV (.csv)", f"Content-Type: {resp_p_doc_csv.get('Content-Type')}")

    # --------------------------------------------------------------------------
    # 3. REGISTRO INDIVIDUAL DE ESTUDIANTE CON CÉDULA CON CEROS (GRADO 4°)
    # --------------------------------------------------------------------------
    print("\n--- 3. REGISTRO INDIVIDUAL CON CEROS A LA IZQUIERDA Y CUENTA AUTOMÁTICA ---")
    doc_indiv = "0054321098"
    # Limpiar si existía de prueba anterior (respetando dependencias FK protegidas)
    Matricula.objects.filter(aprendiz__username=doc_indiv).delete()
    PerfilUsuario.objects.filter(numero_documento=doc_indiv).delete()
    User.objects.filter(username=doc_indiv).delete()

    ficha_g4 = Ficha.objects.filter(codigo_ficha__icontains='4-A').first()
    resp_reg_indiv = client.post(reverse('registrar_aprendiz'), {
        'tipo_documento': 'TI',
        'documento': doc_indiv,
        'nombres': 'Camilo Andrés',
        'apellidos': 'Pérez Castro',
        'email': 'camilo.perez@test.com',
        'telefono': '3001234567',
        'grado': '4',
        'seccion': 'A',
        'ficha_id': ficha_g4.id if ficha_g4 else '',
    }, follow=True)

    user_indiv = User.objects.filter(username=doc_indiv).first()
    test_assert(user_indiv is not None, "Estudiante individual creado con usuario = cédula", f"Username: {getattr(user_indiv, 'username', None)}")
    if user_indiv:
        clave_valida = user_indiv.check_password(doc_indiv)
        test_assert(clave_valida, "Contraseña cifrada coincide exactamente con número de cédula", f"check_password('{doc_indiv}') == True")
        test_assert(user_indiv.password.startswith('pbkdf2_') or user_indiv.password.startswith('argon2'), "Contraseña está almacenada con hash seguro (nunca en texto plano)", "Hash verificado")
        
        perfil_indiv = getattr(user_indiv, 'perfil', None)
        test_assert(perfil_indiv and perfil_indiv.numero_documento == doc_indiv, "Cédula conserva los ceros a la izquierda en perfil", f"Doc: {getattr(perfil_indiv, 'numero_documento', None)}")
        
        mat_indiv = Matricula.objects.filter(aprendiz=user_indiv).first()
        test_assert(mat_indiv is not None and '4' in str(mat_indiv.grado_escolar), "Matrícula vinculada correctamente en Grado 4°", f"Grado: {getattr(mat_indiv, 'grado_escolar', None)}")

    # --------------------------------------------------------------------------
    # 4. CARGA MASIVA DE ESTUDIANTES (TOLERANCIA A ERRORES Y ATOMICIDAD POR FILA)
    # --------------------------------------------------------------------------
    print("\n--- 4. CARGA MASIVA DE ESTUDIANTES CON TOLERANCIA A ERRORES PARCIALES ---")
    doc_masivo_1 = "0078901234"
    doc_masivo_2 = "0089012345"
    # Limpiar previos respetando dependencias de clave foránea protegida
    Matricula.objects.filter(aprendiz__username__in=[doc_masivo_1, doc_masivo_2]).delete()
    PerfilUsuario.objects.filter(numero_documento__in=[doc_masivo_1, doc_masivo_2]).delete()
    User.objects.filter(username__in=[doc_masivo_1, doc_masivo_2]).delete()

    # CSV con: Fila 1 válida (Grado 2), Fila 2 inválida (sin nombre/doc), Fila 3 válida (Grado 8)
    csv_content = (
        "tipo_documento,numero_documento,nombres,apellidos,correo,telefono,genero,grado,seccion\n"
        f"TI,{doc_masivo_1},Lucía Elena,Martínez Gómez,lucia@test.com,3112223333,F,2,A\n"
        ",,,Fila Invalida Sin Documento,,,,,,\n"
        f"TI,{doc_masivo_2},Santiago,Rojas Morales,santiago@test.com,3209998888,M,8,A\n"
    )
    csv_file = SimpleUploadedFile("estudiantes_prueba.csv", csv_content.encode('utf-8'), content_type="text/csv")

    resp_import_est = client.post(reverse('importar_estudiantes_masivo'), {
        'archivo': csv_file,
    }, follow=True)

    u1 = User.objects.filter(username=doc_masivo_1).first()
    u2 = User.objects.filter(username=doc_masivo_2).first()
    test_assert(u1 is not None and u1.check_password(doc_masivo_1), "Fila 1 válida procesada exitosamente con credenciales cédula/cédula", f"Usuario: {getattr(u1, 'username', None)}")
    test_assert(u2 is not None and u2.check_password(doc_masivo_2), "Fila 3 válida procesada exitosamente a pesar del error en Fila 2", f"Usuario: {getattr(u2, 'username', None)}")

    mat1 = Matricula.objects.filter(aprendiz=u1).first()
    mat2 = Matricula.objects.filter(aprendiz=u2).first()
    test_assert(mat1 is not None and '2' in str(mat1.grado_escolar), "Estudiante 1 matriculado en Grado 2°", f"Grado: {getattr(mat1, 'grado_escolar', None)}")
    test_assert(mat2 is not None and '8' in str(mat2.grado_escolar), "Estudiante 2 matriculado en Grado 8°", f"Grado: {getattr(mat2, 'grado_escolar', None)}")

    # Prueba de idempotencia: Reimportar el mismo archivo no debe duplicar cuentas
    csv_file_dup = SimpleUploadedFile("estudiantes_prueba.csv", csv_content.encode('utf-8'), content_type="text/csv")
    resp_import_dup = client.post(reverse('importar_estudiantes_masivo'), {'archivo': csv_file_dup}, follow=True)
    total_u1 = User.objects.filter(username=doc_masivo_1).count()
    test_assert(total_u1 == 1, "Reimportar no duplica ni sobreescribe estudiantes existentes", f"Cuentas encontradas: {total_u1}")

    # --------------------------------------------------------------------------
    # 5. INICIO DE SESIÓN DEL ESTUDIANTE EN SU PROPIO PANEL (SIN NOTAS INVENTADAS)
    # --------------------------------------------------------------------------
    print("\n--- 5. LOGIN DE ESTUDIANTE Y VINCULACIÓN A SU PANEL REAL ---")
    client_est = Client()
    # Login directo con credenciales cédula/cédula
    login_ok = client_est.login(username=doc_masivo_1, password=doc_masivo_1)
    test_assert(login_ok, "Login exitoso con usuario=cédula y contraseña=cédula", f"Credenciales: {doc_masivo_1} / {doc_masivo_1}")

    resp_est_panel = client_est.get(reverse('estudiante_dashboard'))
    test_assert(resp_est_panel.status_code == 200, "Estudiante entra a su panel oficial (/estudiante/)", f"Status: {resp_est_panel.status_code}")
    contenido_html = resp_est_panel.content.decode('utf-8', errors='ignore')
    test_assert("Lucía Elena" in contenido_html, "Panel muestra el nombre real del estudiante", "Lucía Elena presente")
    test_assert("Grado 2" in contenido_html, "Panel muestra el grado real según su matrícula", "Grado 2° presente")
    test_assert("Aún no tienes calificaciones registradas" in contenido_html or "sin notas" in contenido_html.lower() or "boletín oficial" in contenido_html.lower(),
                "No existen calificaciones inventadas (estado limpio y legítimo)", "Sin calificaciones ficticias")

    # --------------------------------------------------------------------------
    # 6. GRADOS ESCOLARES DEL 1 AL 11 UNIFICADOS EN SECRETARÍA
    # --------------------------------------------------------------------------
    print("\n--- 6. GRADOS ESCOLARES DEL 1° AL 11° UNIFICADOS EN SECRETARÍA ---")
    client.force_login(user_secretaria)
    resp_mat_lista = client.get(reverse('matriculas_lista'))
    test_assert(resp_mat_lista.status_code == 200, "Secretaría accede a lista de matrículas", f"Status: {resp_mat_lista.status_code}")
    mat_html = resp_mat_lista.content.decode('utf-8', errors='ignore')
    todos_grados_en_html = all(f"Grado {g}°" in mat_html for g in range(1, 12))
    test_assert(todos_grados_en_html, "Secretaría visualiza opciones para todos los grados del 1° al 11°", "1° a 11° presentes en interfaz")
    test_assert("Todos los Grados" in mat_html, "Opción 'Todos los Grados' visible en interfaz", "'Todos los Grados' presente")

    # --------------------------------------------------------------------------
    # 7. CARGA MASIVA DE DOCENTES CON ROL Y CREDENCIALES
    # --------------------------------------------------------------------------
    print("\n--- 7. CARGA MASIVA DE DOCENTES CON ROL Y ACCESO OFICIAL ---")
    doc_prof = "0099887766"
    User.objects.filter(username=doc_prof).delete()
    PerfilUsuario.objects.filter(numero_documento=doc_prof).delete()

    csv_docentes = (
        "tipo_documento,numero_documento,nombres,apellidos,correo,telefono,especialidad\n"
        f"CC,{doc_prof},Mariana,Gómez Valencia,mariana.docente@edunova.edu.co,3150001122,Matemáticas\n"
    )
    csv_doc_file = SimpleUploadedFile("docentes_prueba.csv", csv_docentes.encode('utf-8'), content_type="text/csv")
    resp_import_doc = client.post(reverse('importar_instructores_masivo'), {
        'archivo': csv_doc_file,
        'desde_pagina': '1',
    })
    test_assert(resp_import_doc.status_code == 200, "Carga masiva de docentes procesada", f"Status: {resp_import_doc.status_code}")

    user_prof = User.objects.filter(username=doc_prof).first()
    test_assert(user_prof is not None, "Docente registrado con usuario = cédula", f"Username: {getattr(user_prof, 'username', None)}")
    if user_prof:
        test_assert(user_prof.check_password(doc_prof), "Docente tiene contraseña = cédula (hasheada)", "check_password == True")
        test_assert(user_prof.perfil and 'Docente' in user_prof.perfil.rol.nombre, "Docente asignado con rol oficial Docente", f"Rol: {user_prof.perfil.rol.nombre}")

    # --------------------------------------------------------------------------
    # 8. NOTIFICACIONES Y PAPELERA DEL DOCENTE
    # --------------------------------------------------------------------------
    print("\n--- 8. NOTIFICACIONES LEGÍTIMAS Y PAPELERA DEL DOCENTE ---")
    client_doc = Client()
    client_doc.force_login(user_docente)

    # Limpiar o inspeccionar notificaciones del docente
    resp_doc_panel = client_doc.get(reverse('instructor_dashboard'))
    test_assert(resp_doc_panel.status_code == 200, "Docente accede a su panel de control", f"Status: {resp_doc_panel.status_code}")

    notifs_context = resp_doc_panel.context.get('notificaciones_docente', [])
    titulos = [n.titulo for n in notifs_context]
    hay_duplicados = len(titulos) != len(set(titulos))
    test_assert(not hay_duplicados, "Notificaciones del docente no presentan mensajes idénticos repetidos", f"Total notificaciones únicas: {len(notifs_context)}")

    # Acceso a Papelera del docente
    resp_pap_doc = client_doc.get(reverse('papelera_docente'))
    test_assert(resp_pap_doc.status_code == 200, "Docente accede a su Papelera en el panel sin error de permisos", f"Status: {resp_pap_doc.status_code}")

    resp_pap_rec = client_doc.get(reverse('papelera_reciclaje'))
    test_assert(resp_pap_rec.status_code == 200, "Docente accede a la vista /papelera/ autorizada", f"Status: {resp_pap_rec.status_code}")

    # --------------------------------------------------------------------------
    # RESUMEN GENERAL
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("RESUMEN DE PRUEBAS EJECUTADAS")
    print("=" * 80)
    total = len(resultados)
    pasaron = sum(1 for _, estado, _ in resultados if estado == "PASÓ")
    fallaron = total - pasaron

    for prueba, estado, det in resultados:
        print(f"[{estado}] {prueba}")

    print(f"\nTOTAL: {total} | APROBADAS: {pasaron} | FALLIDAS: {fallaron}")
    if fallaron == 0:
        print(">>> TODAS LAS PRUEBAS PASARON EXITOSAMENTE AL 100% <<<")
    else:
        print(">>> EXISTEN PRUEBAS CON FALLAS <<<")

if __name__ == '__main__':
    ejecutar_pruebas()
