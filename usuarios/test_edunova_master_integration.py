import re
from datetime import date, time
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from usuarios.models import Rol, PerfilUsuario, FamiliaAcudiente
from academico.models import (
    InstitucionEducativa, ProgramaFormacion, Ficha, Matricula,
    HorarioFicha, CargaAcademica, TareaClase
)
from seguimiento.models import AsistenciaAprendiz, ComunicadoEscolar, MensajeSeguimiento
from evaluaciones.models import JuicioEvaluativo


class EdunovaMasterIntegrationTests(TestCase):
    """
    Suite de integración integral para EduNova:
    1. Login y redirección de los 6 roles institucionales.
    2. Flujo de datos vivo e interconectado (Secretaría -> Docente -> Estudiante -> Familia).
    3. Aislamiento de seguridad y control de accesos prohibidos por URL.
    4. Ausencia total de módulos excluidos visibles en las interfaces.
    """

    def setUp(self):
        # Roles Institucionales
        self.rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador')
        self.rol_rector, _ = Rol.objects.get_or_create(nombre='Rector')
        self.rol_secretaria, _ = Rol.objects.get_or_create(nombre='Secretaría')
        self.rol_docente, _ = Rol.objects.get_or_create(nombre='Docente')
        self.rol_estudiante, _ = Rol.objects.get_or_create(nombre='Estudiante')
        self.rol_familia, _ = Rol.objects.get_or_create(nombre='Familia')

        # Cuentas de los 6 roles
        self.admin_user = User.objects.create_superuser('admin_test', 'admin@edunova.edu', 'Clave-2026')
        self.admin_user.perfil.rol = self.rol_admin
        self.admin_user.perfil.save()

        self.rector_user = User.objects.create_user('rector_test', 'rector@edunova.edu', 'Clave-2026')
        self.rector_user.perfil.rol = self.rol_rector
        self.rector_user.perfil.save()

        self.sec_user = User.objects.create_user('secretaria_test', 'sec@edunova.edu', 'Clave-2026')
        self.sec_user.perfil.rol = self.rol_secretaria
        self.sec_user.perfil.save()

        self.docente_user = User.objects.create_user('docente_test', 'doc@edunova.edu', 'Clave-2026', first_name='Carlos', last_name='Docente')
        self.docente_user.perfil.rol = self.rol_docente
        self.docente_user.perfil.save()

        self.estudiante_user = User.objects.create_user('estudiante_test', 'est@edunova.edu', 'Clave-2026', first_name='Mateo', last_name='Estudiante')
        self.estudiante_user.perfil.rol = self.rol_estudiante
        self.estudiante_user.perfil.numero_documento = '1099887766'
        self.estudiante_user.perfil.save()

        self.familia_user = User.objects.create_user('familia_test', 'fam@edunova.edu', 'Clave-2026', first_name='Maria', last_name='Acudiente')
        self.familia_user.perfil.rol = self.rol_familia
        self.familia_user.perfil.numero_documento = '32112233'
        self.familia_user.perfil.save()

        # Vinculación familiar autorizada
        self.acudiente = FamiliaAcudiente.objects.create(
            nombre_acudiente='Maria Acudiente',
            telefono='3001234567',
            email='fam@edunova.edu'
        )
        self.acudiente.estudiantes.add(self.estudiante_user)

        # Estructura académica base
        self.colegio = InstitucionEducativa.objects.create(
            codigo_dane='147001099999',
            nombre='Colegio Central EduNova',
            municipio='Santa Marta'
        )
        self.programa = ProgramaFormacion.objects.create(
            codigo_programa='1001-A',
            denominacion='Bachillerato Académico'
        )
        self.ficha = Ficha.objects.create(
            codigo_ficha='10-A',
            programa=self.programa,
            institucion=self.colegio,
            instructor_lider=self.docente_user,
            fecha_inicio='2026-02-01',
            fecha_fin='2026-11-30'
        )

        # Matrícula oficial asignada por secretaría
        self.matricula = Matricula.objects.create(
            ficha=self.ficha,
            aprendiz=self.estudiante_user,
            grado_escolar='10',
            seccion='A',
            estado_formacion='En Formacion'
        )

        # Carga académica del docente en grado 10 sección A
        self.carga = CargaAcademica.objects.create(
            profesor=self.docente_user,
            programa=self.programa,
            nivel='Media Tecnica',
            grado='10',
            seccion='A',
            anio_lectivo=2026
        )

        from academico.models import Competencia, ResultadoAprendizaje
        self.competencia = Competencia.objects.create(
            programa=self.programa,
            codigo='MAT-01',
            descripcion='Competencias fundamentales de Matemáticas'
        )
        self.rap = ResultadoAprendizaje.objects.create(
            competencia=self.competencia,
            codigo='RAP-01',
            descripcion='Aplica razonamiento cuantitativo'
        )

    def test_01_login_y_redireccion_seis_roles(self):
        """Comprueba que los 6 roles inician sesión y son dirigidos a sus paneles correctos."""
        client = Client()
        roles_casos = [
            (self.admin_user, '/dashboard/'),
            (self.rector_user, '/rectoria/'),
            (self.sec_user, '/secretaria/'),
            (self.docente_user, '/instructor/'),
            (self.estudiante_user, '/aprendiz/'),
            (self.familia_user, '/familia/'),
        ]
        for user, expected_url in roles_casos:
            client.force_login(user)
            resp = client.get('/accounts/login/')
            self.assertRedirects(resp, expected_url, fetch_redirect_response=False, msg_prefix=f"Fallo en redirección para {user.username}")
            client.logout()

    def test_02_interconexion_docente_ve_estudiante_y_registra_datos(self):
        """Docente asignado ve al estudiante de su grupo y registra calificaciones, asistencia y tareas."""
        self.client.force_login(self.docente_user)

        # Docente consulta sus estudiantes
        resp_estudiantes = self.client.get('/mis-estudiantes/')
        self.assertEqual(resp_estudiantes.status_code, 200)
        self.assertContains(resp_estudiantes, 'Mateo')

        # Docente registra una calificación real
        calif = JuicioEvaluativo.objects.create(
            matricula=self.matricula,
            resultado_aprendizaje=self.rap,
            instructor=self.docente_user,
            fecha_evaluacion=date.today(),
            juicio_valor='A',
            observaciones='Excelente desempeño en evaluación diagnóstica.'
        )

        # Docente registra asistencia
        asist = AsistenciaAprendiz.objects.create(
            matricula=self.matricula,
            fecha=date.today(),
            estado='P',
            registrado_por=self.docente_user,
            observaciones='Asistencia confirmada en clase presencial.'
        )

        # Docente publica tarea
        tarea = TareaClase.objects.create(
            carga_academica=self.carga,
            titulo='Taller de Lectura Crítica 1',
            instrucciones='Desarrollar el análisis de texto y enviar resumen.',
            estado='Publicada'
        )

        # Comprobación de persistencia directa en DB
        self.assertTrue(JuicioEvaluativo.objects.filter(pk=calif.pk).exists())
        self.assertTrue(AsistenciaAprendiz.objects.filter(pk=asist.pk).exists())
        self.assertTrue(TareaClase.objects.filter(pk=tarea.pk).exists())

    def test_03_estudiante_consulta_horario_notas_asistencia_y_tareas_propias(self):
        """El estudiante ve en su panel exactamente sus datos y no de otros."""
        # Creamos horario para su grupo
        HorarioFicha.objects.create(
            ficha=self.ficha,
            instructor=self.docente_user,
            programa=self.programa,
            dia='1',
            hora_inicio=time(7, 0),
            hora_fin=time(8, 30),
            ambiente='Aula 101',
            activo=True
        )
        # Evaluaciones y asistencia
        JuicioEvaluativo.objects.create(
            matricula=self.matricula,
            resultado_aprendizaje=self.rap,
            instructor=self.docente_user,
            fecha_evaluacion=date.today(),
            juicio_valor='A',
            observaciones='Aprobado en periodo 1.'
        )
        AsistenciaAprendiz.objects.create(
            matricula=self.matricula,
            fecha=date.today(),
            estado='P',
            registrado_por=self.docente_user
        )
        TareaClase.objects.create(
            carga_academica=self.carga,
            titulo='Ensayo Histórico 10-A',
            instrucciones='Escribir 2 páginas.',
            estado='Publicada'
        )

        self.client.force_login(self.estudiante_user)
        resp = self.client.get('/aprendiz/')
        self.assertEqual(resp.status_code, 200)

        # Debe contener sus módulos y datos
        self.assertContains(resp, 'Ensayo Histórico 10-A')
        self.assertContains(resp, 'Aula 101')
        self.assertContains(resp, 'Aprobado')
        self.assertContains(resp, 'Carlos Docente')

    def test_04_familia_solo_ve_estudiante_vinculado_y_no_ajenos(self):
        """La familia solo puede consultar la información del estudiante asociado a su acudiente."""
        # Estudiante ajeno
        otro_estudiante = User.objects.create_user('otro_alumno', 'otro@edunova.edu', 'Clave-2026')
        otro_estudiante.perfil.rol = self.rol_estudiante
        otro_estudiante.perfil.numero_documento = '999888777'
        otro_estudiante.perfil.save()
        Matricula.objects.create(
            ficha=self.ficha,
            aprendiz=otro_estudiante,
            grado_escolar='10',
            seccion='A'
        )

        self.client.force_login(self.familia_user)
        session = self.client.session
        session['estudiante_fam_doc'] = self.estudiante_user.perfil.numero_documento
        session.save()

        resp_portal = self.client.get('/familia/')
        self.assertEqual(resp_portal.status_code, 200)
        self.assertContains(resp_portal, 'Mateo')
        self.assertNotContains(resp_portal, 'otro_alumno')

    def test_05_seguridad_bloqueo_accesos_prohibidos_directos(self):
        """Verifica que el estudiante no acceda a paneles de otros roles por URL directa."""
        self.client.force_login(self.estudiante_user)

        rutas_prohibidas = [
            '/dashboard/',
            '/rectoria/',
            '/secretaria/',
            '/instructor/',
            '/usuarios/',
            '/configuracion/',
        ]
        for ruta in rutas_prohibidas:
            resp = self.client.get(ruta)
            # Debe redirigir o dar 403
            self.assertIn(resp.status_code, [302, 403], f"La ruta {ruta} no bloqueó al estudiante.")

    def test_06_ausencia_total_de_modulos_excluidos_en_vistas_visibles(self):
        """Verifica que ninguna de las pantallas principales contenga botones o menciones a las funciones excluidas."""
        usuarios_a_probar = [
            (self.admin_user, '/dashboard/'),
            (self.rector_user, '/rectoria/'),
            (self.sec_user, '/secretaria/'),
            (self.docente_user, '/instructor/'),
            (self.estudiante_user, '/aprendiz/'),
            (self.familia_user, '/familia/'),
        ]

        terminos_prohibidos = [
            'pensiones',
            'transporte escolar',
            'rutas escolares',
            'facturación',
            'centro financiero',
            'carnet digital',
            'escanear carnet',
        ]

        for user, ruta in usuarios_a_probar:
            self.client.force_login(user)
            resp = self.client.get(ruta)
            self.assertEqual(resp.status_code, 200, f"Error cargando {ruta} con {user.username}")
            contenido = resp.content.decode('utf-8', errors='ignore').lower()

            for termino in terminos_prohibidos:
                # Quitamos comentarios html para verificar visibilidad
                contenido_sin_comentarios = re.sub(r'<!--.*?-->', '', contenido, flags=re.DOTALL)
                self.assertNotIn(
                    termino,
                    contenido_sin_comentarios,
                    f"Término prohibido visible '{termino}' encontrado en {ruta} para {user.username}"
                )
            self.client.logout()
