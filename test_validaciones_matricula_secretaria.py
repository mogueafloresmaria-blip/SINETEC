import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sinetec_project.settings')
django.setup()

from django.test import RequestFactory, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from academico.models import Matricula, Ficha
from usuarios.models import PerfilUsuario, Rol
from academico.views import nueva_matricula


def setup_request(request, user):
    request.user = user
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()
    setattr(request, '_messages', FallbackStorage(request))
    return request


def run_all_8_tests():
    print("=" * 80)
    print("SUITE DE PRUEBAS DE VALIDACIÓN: SECRETARÍA - MATRÍCULAS EDUNOVA")
    print("=" * 80)

    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(perfil__rol__nombre__in=['Administrador', 'Secretaría']).first()
    assert admin_user, "Usuario administrativo requerido para las pruebas."

    rf = RequestFactory()
    url = reverse('nueva_matricula')
    resultados = {}

    # -------------------------------------------------------------------------
    # PRUEBA 1: Intentar registrar un estudiante sin número de documento
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Intentar registrar un estudiante sin número de documento...")
    data_t1 = {
        'modo_registro': 'nuevo',
        'documento': '',
        'nombre': 'Estudiante Uno',
        'apellido': 'Prueba SinDoc',
        'email': 'estudiante1@edunova.edu',
        'grado_escolar': '10',
        'seccion': 'A',
        'jornada': 'Mañana',
        'anio_lectivo': '2026',
    }
    req1 = rf.post(url, data=data_t1)
    setup_request(req1, admin_user)
    resp1 = nueva_matricula(req1)
    # Debe rechazar: status 200 re-renderizando con errores, no 302
    assert resp1.status_code == 200, f"Error en status code: {resp1.status_code}"
    html1 = resp1.content.decode('utf-8')
    assert 'El número de documento es obligatorio' in html1 or 'is-invalid' in html1, "No se detectó el error de documento obligatorio"
    assert not User.objects.filter(first_name='Estudiante Uno', last_name='Prueba SinDoc').exists()
    print("  -> PASÓ: Rechazado con éxito. No se creó estudiante y se mostró mensaje de error debajo del documento.")
    resultados['Prueba 1: Sin número de documento'] = 'APROBADA (Cumple)'

    # -------------------------------------------------------------------------
    # PRUEBA 2: Introducir letras en el documento
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Introducir letras o símbolos en el documento...")
    data_t2 = {
        'modo_registro': 'nuevo',
        'documento': '1098ABC765',
        'nombre': 'Estudiante Dos',
        'apellido': 'Prueba LetrasDoc',
        'email': 'estudiante2@edunova.edu',
        'grado_escolar': '10',
        'seccion': 'A',
        'jornada': 'Mañana',
        'anio_lectivo': '2026',
    }
    req2 = rf.post(url, data=data_t2)
    setup_request(req2, admin_user)
    resp2 = nueva_matricula(req2)
    assert resp2.status_code == 200
    html2 = resp2.content.decode('utf-8')
    assert 'El documento debe contener únicamente números' in html2 or 'is-invalid' in html2
    assert not User.objects.filter(username='1098ABC765').exists()
    print("  -> PASÓ: Rechazado con éxito. El sistema exigió solo dígitos numéricos sin letras ni símbolos.")
    resultados['Prueba 2: Letras en el documento'] = 'APROBADA (Cumple)'

    # -------------------------------------------------------------------------
    # PRUEBA 3: Introducir un correo electrónico incorrecto
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Introducir correos electrónicos incorrectos (aminta@gmail, aminta.com, aminta@@gmail.com)...")
    correos_invalidos = ['aminta@gmail', 'aminta.com', 'aminta@@gmail.com', 'aminta@gmail..com']
    for bad_email in correos_invalidos:
        data_t3 = {
            'modo_registro': 'nuevo',
            'documento': '9900112233',
            'nombre': 'Estudiante Tres',
            'apellido': 'Prueba BadEmail',
            'email': bad_email,
            'grado_escolar': '10',
            'seccion': 'A',
            'jornada': 'Mañana',
            'anio_lectivo': '2026',
        }
        req3 = rf.post(url, data=data_t3)
        setup_request(req3, admin_user)
        resp3 = nueva_matricula(req3)
        assert resp3.status_code == 200
        html3 = resp3.content.decode('utf-8')
        assert 'correo electrónico no tiene un formato válido' in html3 or 'is-invalid' in html3
        assert not User.objects.filter(username='9900112233').exists()
        print(f"    Subcaso '{bad_email}': Rechazado correctamente con mensaje formativo.")
    print("  -> PASÓ: Todos los correos inválidos fueron rechazados y resaltados en rojo.")
    resultados['Prueba 3: Correo electrónico incorrecto'] = 'APROBADA (Cumple)'

    # -------------------------------------------------------------------------
    # PRUEBA 4: Dejar nombres o apellidos vacíos o compuestos únicamente por números
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Dejar nombres o apellidos vacíos o con números únicamente...")
    casos_nom_ape = [
        ('', 'Rodríguez', 'Nombres vacíos'),
        ('Carlos Andrés', '', 'Apellidos vacíos'),
        ('123456', 'Rodríguez', 'Nombres con solo números'),
        ('Carlos Andrés', '789012', 'Apellidos con solo números'),
    ]
    for nom, ape, desc in casos_nom_ape:
        data_t4 = {
            'modo_registro': 'nuevo',
            'documento': '9900223344',
            'nombre': nom,
            'apellido': ape,
            'email': 'valido@edunova.edu',
            'grado_escolar': '10',
            'seccion': 'A',
            'jornada': 'Mañana',
            'anio_lectivo': '2026',
        }
        req4 = rf.post(url, data=data_t4)
        setup_request(req4, admin_user)
        resp4 = nueva_matricula(req4)
        assert resp4.status_code == 200
        assert not User.objects.filter(username='9900223344').exists()
        print(f"    Subcaso {desc}: Rechazado correctamente sin guardar.")
    print("  -> PASÓ: Nombres y apellidos validados como obligatorios y con letras reales.")
    resultados['Prueba 4: Nombres o apellidos vacíos/números'] = 'APROBADA (Cumple)'

    # -------------------------------------------------------------------------
    # PRUEBA 5: No seleccionar grado, grupo o jornada
    # -------------------------------------------------------------------------
    print("\n[TEST 5] No seleccionar grado, grupo o jornada...")
    casos_academicos = [
        ('', 'A', 'Mañana', 'Sin grado escolar'),
        ('10', '', 'Mañana', 'Sin grupo/sección'),
        ('10', 'A', '', 'Sin jornada escolar'),
    ]
    for g, s, j, desc in casos_academicos:
        data_t5 = {
            'modo_registro': 'nuevo',
            'documento': '9900334455',
            'nombre': 'Estudiante Cinco',
            'apellido': 'Prueba Academicos',
            'email': 'est5@edunova.edu',
            'grado_escolar': g,
            'seccion': s,
            'jornada': j,
            'anio_lectivo': '2026',
        }
        req5 = rf.post(url, data=data_t5)
        setup_request(req5, admin_user)
        resp5 = nueva_matricula(req5)
        assert resp5.status_code == 200
        assert not User.objects.filter(username='9900334455').exists()
        print(f"    Subcaso {desc}: Rechazado correctamente.")
    print("  -> PASÓ: Grado, sección y jornada son estrictamente obligatorios.")
    resultados['Prueba 5: No seleccionar grado, grupo o jornada'] = 'APROBADA (Cumple)'

    # -------------------------------------------------------------------------
    # PRUEBA 6: Intentar registrar un documento que ya exista
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Intentar registrar un documento que ya exista...")
    # Carla Flores ya existe en BD con documento 1745637476
    doc_carla = '1745637476'
    carla = User.objects.filter(username=doc_carla).first()
    assert carla is not None, "Carla Flores debe existir para esta prueba."

    data_t6 = {
        'modo_registro': 'nuevo',
        'documento': doc_carla,
        'nombre': 'Carla Clon',
        'apellido': 'Flores Duplicada',
        'email': 'carla.clon@edunova.edu',
        'grado_escolar': '10',
        'seccion': 'A',
        'jornada': 'Mañana',
        'anio_lectivo': '2026',
    }
    req6 = rf.post(url, data=data_t6)
    setup_request(req6, admin_user)
    resp6 = nueva_matricula(req6)
    assert resp6.status_code == 200
    html6 = resp6.content.decode('utf-8')
    assert 'Ya existe un estudiante registrado con el documento' in html6 or 'is-invalid' in html6
    # Comprobar que no se alteró a Carla ni se duplicó
    assert User.objects.filter(username=doc_carla).count() == 1
    carla_check = User.objects.get(username=doc_carla)
    assert carla_check.first_name != 'Carla Clon', "El usuario existente fue sobrescrito erróneamente."
    print("  -> PASÓ: Documento duplicado bloqueado. No se sobrescribió al estudiante existente.")
    resultados['Prueba 6: Registrar documento ya existente'] = 'APROBADA (Cumple)'

    # -------------------------------------------------------------------------
    # PRUEBA 7: Intentar asignar una matrícula duplicada
    # -------------------------------------------------------------------------
    print("\n[TEST 7] Intentar asignar una matrícula duplicada...")
    # Usar un estudiante con matrícula activa en 10°A 2026
    est_dup_doc = '9977889900'
    est_dup = User.objects.filter(username=est_dup_doc).first()
    if not est_dup:
        rol_e, _ = Rol.objects.get_or_create(nombre='Estudiante')
        est_dup = User.objects.create_user(
            username=est_dup_doc,
            first_name='Estudiante',
            last_name='Matrícula Duplicada',
            email=f'{est_dup_doc}@edunova.edu',
            password=est_dup_doc
        )
        PerfilUsuario.objects.get_or_create(usuario=est_dup, defaults={'rol': rol_e, 'numero_documento': est_dup_doc})

    Matricula.objects.filter(aprendiz=est_dup).delete()
    ficha_10a = Ficha.objects.filter(codigo_ficha__icontains='COL-2026-G10-A').first() or Ficha.objects.first()
    mat_inicial = Matricula.objects.create(
        aprendiz=est_dup,
        ficha=ficha_10a,
        grado_escolar='10',
        seccion='A',
        estado_formacion='En Formacion'
    )

    # Intentar asignar exactamente la misma matrícula (10°A 2026) al mismo estudiante
    data_t7 = {
        'modo_registro': 'existente',
        'alumno_id': str(est_dup.pk),
        'grado_escolar': '10',
        'seccion': 'A',
        'jornada': 'Mañana',
        'anio_lectivo': '2026',
    }
    req7 = rf.post(url, data=data_t7)
    setup_request(req7, admin_user)
    resp7 = nueva_matricula(req7)
    # Debe ser rechazada (status 200 en el formulario, sin redirección ni duplicado)
    assert resp7.status_code == 200, f"Status code inesperado: {resp7.status_code}"
    html7 = resp7.content.decode('utf-8')
    assert 'No se permiten matrículas duplicadas' in html7 or 'ya cuenta con una matrícula activa' in html7, "No se mostró mensaje de matrícula duplicada"
    assert Matricula.objects.filter(aprendiz=est_dup, estado_formacion='En Formacion').count() == 1, "Se creó una matrícula duplicada en la base de datos."
    print("  -> PASÓ: Matrícula duplicada rechazada con éxito y advertencia visual mostrada.")
    resultados['Prueba 7: Asignar matrícula duplicada'] = 'APROBADA (Cumple)'

    # -------------------------------------------------------------------------
    # PRUEBA 8: Comprobar que un formulario con datos correctos sí permita guardar
    # -------------------------------------------------------------------------
    print("\n[TEST 8] Comprobar que un formulario con datos correctos sí permita guardar...")
    doc_valido = '9988112233'
    # Limpieza previa
    Matricula.objects.filter(aprendiz__username=doc_valido).delete()
    User.objects.filter(username=doc_valido).delete()

    data_t8 = {
        'modo_registro': 'nuevo',
        'documento': doc_valido,
        'nombre': 'Valeria Sofía',
        'apellido': 'Martínez Peña',
        'email': 'valeria.martinez@edunova.edu',
        'grado_escolar': '10',
        'seccion': 'B',
        'jornada': 'Tarde',
        'anio_lectivo': '2027',
    }
    req8 = rf.post(url, data=data_t8)
    setup_request(req8, admin_user)
    resp8 = nueva_matricula(req8)
    # Debe redirigir con éxito (status 302 hacia matriculas_lista)
    assert resp8.status_code == 302, f"Error al guardar datos válidos, status: {resp8.status_code}"
    assert resp8.url == reverse('matriculas_lista')

    # Validar creación en base de datos
    nuevo_u = User.objects.filter(username=doc_valido).first()
    assert nuevo_u is not None, "El estudiante con datos válidos no fue creado."
    assert nuevo_u.first_name == 'Valeria Sofía'
    assert nuevo_u.last_name == 'Martínez Peña'
    mat_creada = Matricula.objects.filter(aprendiz=nuevo_u, estado_formacion='En Formacion').first()
    assert mat_creada is not None, "La matrícula no fue guardada en MySQL."
    assert mat_creada.grado_escolar == '10'
    assert mat_creada.seccion == 'B'
    assert "2027" in mat_creada.ficha.codigo_ficha or mat_creada.ficha.fecha_inicio.year == 2027
    print(f"  -> PASÓ: Estudiante {nuevo_u.get_full_name()} matriculado exitosamente en Grado 10°B Año 2027 (ID #{mat_creada.id}).")
    resultados['Prueba 8: Formulario con datos correctos permite guardar'] = 'APROBADA (Cumple)'

    # Limpieza final de registros de prueba
    Matricula.objects.filter(aprendiz__in=[est_dup, nuevo_u]).delete()
    User.objects.filter(id__in=[est_dup.id, nuevo_u.id]).delete()

    print("\n" + "=" * 80)
    print("RESUMEN DE LAS 8 PRUEBAS SOLICITADAS:")
    print("=" * 80)
    all_ok = True
    for prueba, estado in resultados.items():
        print(f"  {prueba}: {estado}")
        if 'APROBADA' not in estado:
            all_ok = False

    print("=" * 80)
    if all_ok:
        print("RESULTADO FINAL: LAS 8 PRUEBAS FUERON APROBADAS AL 100% SIN ERRORES.")
    else:
        print("RESULTADO FINAL: EXISTEN ERRORES PENDIENTES.")
    print("=" * 80)


if __name__ == '__main__':
    run_all_8_tests()

