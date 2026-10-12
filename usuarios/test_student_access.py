from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from academico.models import (
    CargaAcademica,
    Ficha,
    Matricula,
    ProgramaFormacion,
    ProyectoInnovacion,
    TareaClase,
)
from instituciones.models import InstitucionEducativa
from seguimiento.models import EtapaProductiva, SolicitudSecretaria
from usuarios.models import Rol


class StudentAccessFlowTests(TestCase):
    def setUp(self):
        self.student_role, _ = Rol.objects.get_or_create(nombre='Estudiante')
        self.teacher_role, _ = Rol.objects.get_or_create(nombre='Instructor SENA')
        self.student = User.objects.create_user(
            username='estudiante_prueba',
            password='ClaveSegura-2026',
            first_name='Estudiante',
            last_name='Prueba',
        )
        self.student.perfil.__class__.objects.filter(usuario=self.student).update(
            rol=self.student_role,
            numero_documento='1002003004',
        )
        self.teacher = User.objects.create_user(
            username='docente_prueba',
            password='ClaveSegura-2026',
        )
        self.teacher.perfil.__class__.objects.filter(usuario=self.teacher).update(
            rol=self.teacher_role,
        )

        self.school = InstitucionEducativa.objects.create(
            codigo_dane='147001000777',
            nombre='Institución de Prueba',
            municipio='Aracataca',
        )
        self.program = ProgramaFormacion.objects.create(
            codigo_programa='228106',
            denominacion='Técnico en Sistemas',
        )
        self.ficha = Ficha.objects.create(
            codigo_ficha='2501452',
            programa=self.program,
            institucion=self.school,
            instructor_lider=self.teacher,
            fecha_inicio='2026-02-01',
            fecha_fin='2027-11-30',
        )
        self.matricula = Matricula.objects.create(
            ficha=self.ficha,
            aprendiz=self.student,
            grado_escolar='10',
            seccion='A',
        )
        self.carga = CargaAcademica.objects.create(
            profesor=self.teacher,
            programa=self.program,
            nivel='Secundaria',
            grado='10°',
            seccion='A',
        )
        self.tarea_asignada = TareaClase.objects.create(
            carga_academica=self.carga,
            titulo='Actividad del grupo',
            instrucciones='Resolver la actividad.',
            estado='Publicada',
        )
        self.tarea_borrador = TareaClase.objects.create(
            carga_academica=self.carga,
            titulo='Borrador docente',
            instrucciones='No debe aparecer al estudiante.',
            estado='Borrador',
        )
        carga_ajena = CargaAcademica.objects.create(
            profesor=self.teacher,
            programa=self.program,
            nivel='Secundaria',
            grado='11',
            seccion='A',
        )
        self.tarea_ajena = TareaClase.objects.create(
            carga_academica=carga_ajena,
            titulo='Actividad de otro grado',
            instrucciones='No asignada a este estudiante.',
            estado='Publicada',
        )

    def test_login_por_documento_dirige_al_portal_del_estudiante(self):
        response = self.client.post('/accounts/login/', {
            'username': '1002003004',
            'password': 'ClaveSegura-2026',
        })

        self.assertRedirects(response, '/aprendiz/', fetch_redirect_response=False)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_acceso_demo_estudiante_abre_su_panel_sin_credenciales(self):
        with override_settings(DEBUG=True):
            response = self.client.post('/accounts/login/', {
                'demo_access': 'student',
            })

        self.assertRedirects(response, '/aprendiz/', fetch_redirect_response=False)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'demo_estudiante')
        self.assertEqual(response.wsgi_request.user.perfil.rol, self.student_role)
        self.assertFalse(response.wsgi_request.user.has_usable_password())
        self.assertTrue(response.wsgi_request.user.perfil.esta_activo)
        cuenta_id = response.wsgi_request.user.pk

        dashboard = self.client.get('/aprendiz/')

        self.assertEqual(dashboard.status_code, 200)
        self.assertIsNone(dashboard.context['matricula'])
        self.client.logout()
        with override_settings(DEBUG=True):
            respuesta_repetida = self.client.post('/accounts/login/', {
                'demo_access': 'student',
            })
        self.assertEqual(respuesta_repetida.wsgi_request.user.pk, cuenta_id)
        self.assertEqual(User.objects.filter(username='demo_estudiante').count(), 1)

    def test_acceso_demo_estudiante_no_funciona_fuera_de_debug(self):
        with override_settings(DEBUG=False):
            response = self.client.post('/accounts/login/', {
                'demo_access': 'student',
            })

        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertFalse(User.objects.filter(username='demo_estudiante').exists())

    def test_acceso_demo_estudiante_rechaza_cuenta_con_otro_rol(self):
        cuenta_demo = User.objects.create_user(username='demo_estudiante', password='clave-interna-demo')
        cuenta_demo.perfil.rol = self.teacher_role
        cuenta_demo.perfil.save(update_fields=['rol'])

        with override_settings(DEBUG=True):
            response = self.client.post('/accounts/login/', {
                'demo_access': 'student',
            })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'La cuenta estudiantil de demostración no está disponible.')
        cuenta_demo.refresh_from_db()
        self.assertTrue(cuenta_demo.has_usable_password())
        self.assertEqual(cuenta_demo.perfil.rol, self.teacher_role)

    def test_acceso_demo_no_suplantara_usuario_estudiante_con_contrasena(self):
        cuenta_demo = User.objects.create_user(username='demo_estudiante', password='clave-interna-demo')
        cuenta_demo.perfil.rol = self.student_role
        cuenta_demo.perfil.save(update_fields=['rol'])

        with override_settings(DEBUG=True):
            response = self.client.post('/accounts/login/', {
                'demo_access': 'student',
            })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'La cuenta estudiantil de demostración no está disponible.')
        self.assertTrue(cuenta_demo.check_password('clave-interna-demo'))

    def test_cuenta_estudiantil_inactiva_no_inicia_sesion(self):
        self.student.perfil.__class__.objects.filter(usuario=self.student).update(
            esta_activo=False,
        )

        response = self.client.post('/accounts/login/', {
            'username': self.student.username,
            'password': 'ClaveSegura-2026',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_dashboard_muestra_modulos_y_datos_asignados(self):
        self.client.force_login(self.student)

        response = self.client.get('/aprendiz/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="student-home-content"')
        self.assertContains(response, 'id="estudianteTabsContent"')
        self.assertContains(response, 'tab-content d-none')
        self.assertContains(response, 'hidden')
        self.assertContains(response, 'id="student-nav-home"')
        self.assertContains(response, 'id="student-nav-calificaciones"')
        self.assertContains(response, 'id="student-nav-horario"')
        self.assertContains(response, 'id="student-nav-actividades"')
        self.assertContains(response, 'id="student-nav-asistencia"')
        self.assertNotContains(response, 'id="estudianteTabs"')
        self.assertNotContains(response, 'stat-kpi-clickable')
        self.assertEqual([tarea.id for tarea in response.context['tareas_clase']], [
            self.tarea_asignada.id,
        ])
        self.assertEqual(response.context['ficha'], self.ficha)

    def test_vista_y_entrega_de_tareas_solo_incluyen_tareas_publicadas_asignadas(self):
        self.client.force_login(self.student)

        response = self.client.get('/academico/mis-actividades/')

        self.assertEqual(response.status_code, 200)
        tareas = [item['tarea'].id for item in response.context['tareas']]
        self.assertEqual(tareas, [self.tarea_asignada.id])
        respuesta_ajena = self.client.get(
            f'/academico/tarea/{self.tarea_ajena.id}/entregar/'
        )
        self.assertEqual(respuesta_ajena.status_code, 404)
        respuesta_borrador = self.client.get(
            f'/academico/tarea/{self.tarea_borrador.id}/entregar/'
        )
        self.assertEqual(respuesta_borrador.status_code, 404)

    def test_modulos_complementarios_del_estudiante_cargan_con_su_sesion(self):
        self.client.force_login(self.student)

        for nombre_ruta in (
            'biblioteca_formacion',
            'notificaciones_lista',
            'portafolio_aprendiz',
        ):
            with self.subTest(ruta=nombre_ruta):
                response = self.client.get(reverse(nombre_ruta))
                self.assertEqual(response.status_code, 200)

    def test_estudiante_no_accede_a_funciones_docentes_ni_dashboard_administrativo(self):
        self.client.force_login(self.student)

        respuesta_clase = self.client.get(f'/academico/clase/{self.carga.id}/')
        respuesta_panel = self.client.get('/dashboard/')
        respuesta_fichas = self.client.get('/academico/fichas/')
        respuesta_seguimiento = self.client.get('/seguimiento/')
        respuesta_secretaria = self.client.get('/seguimiento/secretaria/')

        self.assertRedirects(respuesta_clase, '/aprendiz/', fetch_redirect_response=False)
        self.assertRedirects(respuesta_panel, '/aprendiz/', fetch_redirect_response=False)
        self.assertRedirects(respuesta_fichas, '/aprendiz/', fetch_redirect_response=False)
        self.assertRedirects(respuesta_seguimiento, '/aprendiz/', fetch_redirect_response=False)
        self.assertRedirects(respuesta_secretaria, '/aprendiz/', fetch_redirect_response=False)

    def test_estudiante_no_accede_a_gestion_administrativa_ni_a_sus_apis(self):
        self.client.force_login(self.student)

        nombres_ruta_restringida = (
            'redactar_circular',
            'caja_pensiones',
            'familias_lista',
            'transporte_escolar',
            'estudiante_editar',
            'estudiante_cambiar_estado',
            'estudiante_eliminar',
            'api_sena_guardar_asistencia',
            'api_sena_registrar_aprendiz',
            'api_sena_generar_ia',
            'api_sena_exportar_datos',
        )

        for nombre_ruta in nombres_ruta_restringida:
            with self.subTest(ruta=nombre_ruta):
                response = self.client.get(
                    reverse(nombre_ruta, kwargs={'pk': self.student.pk})
                    if nombre_ruta in {'estudiante_editar', 'estudiante_cambiar_estado', 'estudiante_eliminar'}
                    else reverse(nombre_ruta)
                )
                self.assertRedirects(
                    response,
                    '/aprendiz/',
                    fetch_redirect_response=False,
                )

    def test_alias_alumno_solo_ve_sus_etapas_y_proyectos_asignados(self):
        self.student_role.nombre = 'Alumno'
        self.student_role.save(update_fields=['nombre'])
        otra_ficha = Ficha.objects.create(
            codigo_ficha='2501455',
            programa=self.program,
            institucion=self.school,
            instructor_lider=self.teacher,
            fecha_inicio='2026-02-01',
            fecha_fin='2027-11-30',
        )
        otro_estudiante = User.objects.create_user(username='otro_aprendiz')
        otra_matricula = Matricula.objects.create(
            ficha=otra_ficha,
            aprendiz=otro_estudiante,
            grado_escolar='10',
            seccion='A',
        )
        etapa_ajena = EtapaProductiva.objects.create(
            matricula=otra_matricula,
            instructor_seguimiento=self.teacher,
        )
        proyecto_ajeno = ProyectoInnovacion.objects.create(
            titulo='Proyecto de otra ficha',
            descripcion='No debe aparecer para este estudiante.',
            lider=self.teacher,
            ficha=otra_ficha,
        )
        self.client.force_login(self.student)

        etapas_response = self.client.get(reverse('etapa_productiva_dashboard'))
        proyectos_response = self.client.get(reverse('innovacion_dashboard'))
        detalle_response = self.client.get(
            reverse('innovacion_proyecto_detalle', kwargs={'pk': proyecto_ajeno.pk})
        )

        self.assertEqual(etapas_response.status_code, 200)
        self.assertEqual(list(etapas_response.context['etapas']), [])
        self.assertEqual(proyectos_response.status_code, 200)
        self.assertNotIn(proyecto_ajeno, proyectos_response.context['proyectos'])
        self.assertEqual(detalle_response.status_code, 404)
        self.assertTrue(EtapaProductiva.objects.filter(pk=etapa_ajena.pk).exists())

    def test_libreta_de_calificaciones_solo_permite_consultar_datos_propios(self):
        otro_estudiante = User.objects.create_user(username='otro_estudiante')
        otro_estudiante.perfil.__class__.objects.filter(usuario=otro_estudiante).update(
            rol=self.student_role,
        )
        Matricula.objects.create(
            ficha=self.ficha,
            aprendiz=otro_estudiante,
            grado_escolar='10',
            seccion='A',
        )
        self.client.force_login(self.student)

        respuesta_propia = self.client.get(
            f'/evaluaciones/libreta/{self.student.pk}/'
        )
        respuesta_ajena = self.client.get(
            f'/evaluaciones/libreta/{otro_estudiante.pk}/'
        )

        self.assertEqual(respuesta_propia.status_code, 200)
        self.assertEqual(respuesta_ajena.status_code, 403)

    def test_estudiante_no_puede_publicar_comunicados(self):
        self.client.force_login(self.student)

        response = self.client.post('/comunicaciones/', {
            'destinatario_tipo': 'Toda',
            'asunto': 'Intento de comunicado',
            'mensaje': 'Este mensaje no debe publicarse como comunicado institucional.',
        })

        self.assertRedirects(response, '/comunicaciones/', fetch_redirect_response=False)
        self.assertFalse(
            self.student.comunicados_publicados.filter(
                asunto='Intento de comunicado',
            ).exists()
        )

    def test_solicitud_estudiantil_solo_usa_su_matricula(self):
        otra_ficha = Ficha.objects.create(
            codigo_ficha='2501453',
            programa=self.program,
            institucion=self.school,
            instructor_lider=self.teacher,
            fecha_inicio='2026-02-01',
            fecha_fin='2027-11-30',
        )
        self.client.force_login(self.student)

        respuesta_formulario = self.client.get('/seguimiento/secretaria/solicitud/nueva/')
        respuesta_post = self.client.post('/seguimiento/secretaria/solicitud/nueva/', {
            'asunto': 'Solicitud de prueba',
            'categoria': 'Academica',
            'prioridad': 'Media',
            'mensaje': 'Solicitud para una ficha ajena.',
            'ficha_id': str(otra_ficha.pk),
        })

        self.assertEqual(respuesta_formulario.status_code, 200)
        self.assertEqual(list(respuesta_formulario.context['fichas']), [self.ficha])
        self.assertRedirects(
            respuesta_post,
            '/seguimiento/secretaria/solicitud/nueva/',
            fetch_redirect_response=False,
        )
        self.assertFalse(SolicitudSecretaria.objects.filter(aprendiz=self.student).exists())

    def test_semaforo_estudiantil_solo_muestra_su_ficha_y_no_admite_cambios(self):
        self.client.force_login(self.student)

        respuesta_propia = self.client.get(
            '/evaluaciones/semaforo/',
            {'ficha': self.ficha.pk},
        )
        respuesta_ajena = self.client.get(
            '/evaluaciones/semaforo/',
            {'ficha': self.ficha.pk + 999},
        )
        respuesta_cambio = self.client.post(
            '/evaluaciones/semaforo/api/actualizar/',
            {'matricula_id': self.matricula.pk, 'competencia_id': 1, 'estado': 'APROBADO'},
        )

        self.assertEqual(respuesta_propia.status_code, 200)
        self.assertEqual(respuesta_ajena.status_code, 404)
        self.assertRedirects(respuesta_cambio, '/aprendiz/', fetch_redirect_response=False)

    def test_certificacion_estudiantil_solo_muestra_su_matricula(self):
        otra_ficha = Ficha.objects.create(
            codigo_ficha='2501454',
            programa=self.program,
            institucion=self.school,
            instructor_lider=self.teacher,
            fecha_inicio='2026-02-01',
            fecha_fin='2027-11-30',
        )
        self.client.force_login(self.student)

        respuesta_propia = self.client.get(
            '/academico/certificacion/',
            {'ficha': self.ficha.pk},
        )
        respuesta_ajena = self.client.get(
            '/academico/certificacion/',
            {'ficha': otra_ficha.pk},
        )

        self.assertEqual(respuesta_propia.status_code, 200)
        self.assertEqual(
            [item['matricula'].aprendiz_id for item in respuesta_propia.context['aprendices_cert']],
            [self.student.pk],
        )
        self.assertEqual(respuesta_ajena.context['ficha_seleccionada'], self.ficha)
        self.assertEqual(
            [item['matricula'].aprendiz_id for item in respuesta_ajena.context['aprendices_cert']],
            [self.student.pk],
        )
