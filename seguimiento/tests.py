from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from instituciones.models import InstitucionEducativa
from academico.models import ProgramaFormacion, Ficha, Matricula
from .models import AsistenciaAprendiz, BitacoraSeguimiento


class SeguimientoModelTest(TestCase):
    def setUp(self):
        self.colegio = InstitucionEducativa.objects.create(
            codigo_dane="147001000999",
            nombre="I.E. Simón Bolívar",
            municipio="Santa Marta"
        )
        self.programa = ProgramaFormacion.objects.create(
            codigo_programa="228106",
            denominacion="Técnico en Sistemas"
        )
        self.instructor = User.objects.create_user(
            username="inst_andrea",
            first_name="Andrea",
            last_name="Gómez"
        )
        self.ficha = Ficha.objects.create(
            codigo_ficha="2501890",
            programa=self.programa,
            institucion=self.colegio,
            instructor_lider=self.instructor,
            fecha_inicio="2026-02-01",
            fecha_fin="2027-11-30"
        )

    def test_bitacora_grupal_sin_novedades(self):
        """Verifica el guardado de una bitácora grupal estándar"""
        bitacora = BitacoraSeguimiento.objects.create(
            ficha=self.ficha,
            instructor=self.instructor,
            fecha_visita="2026-09-14",
            tipo_seguimiento="Presencial Aula",
            observaciones="Sesión formativa sin novedades. Excelente avance en algoritmos."
        )
        self.assertIsNotNone(bitacora.id)
        self.assertIsNone(bitacora.matricula)

    def test_regla_rn006_compromisos_exigen_fecha_verificacion(self):
        """Verifica la regla RN-006: Si hay compromisos, debe existir fecha de verificación"""
        bitacora = BitacoraSeguimiento(
            ficha=self.ficha,
            instructor=self.instructor,
            fecha_visita="2026-09-14",
            tipo_seguimiento="Presencial Aula",
            observaciones="Bajo rendimiento en el taller de redes.",
            compromisos="Presentar taller de recuperación.",
            fecha_verificacion=None  # Falta la fecha obligatoria
        )
        with self.assertRaises(ValidationError):
            bitacora.full_clean()

    def test_lista_marca_compromiso_vencido(self):
        bitacora = BitacoraSeguimiento.objects.create(
            ficha=self.ficha,
            instructor=self.instructor,
            fecha_visita='2026-09-01',
            tipo_seguimiento='Presencial Aula',
            observaciones='Seguimiento con compromiso pendiente.',
            compromisos='Entregar plan de mejora.',
            fecha_verificacion=timezone.localdate() - timedelta(days=1),
        )
        self.client.force_login(self.instructor)

        response = self.client.get('/seguimiento/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vencido')
        self.assertContains(response, str(bitacora.fecha_verificacion.strftime('%d/%m/%Y')))

    def test_descargar_acta_pdf_incluye_datos_y_firmas(self):
        self.colegio.enlace_nombre = 'Docente Enlace Prueba'
        self.colegio.save(update_fields=['enlace_nombre'])
        bitacora = BitacoraSeguimiento.objects.create(
            ficha=self.ficha,
            instructor=self.instructor,
            fecha_visita='2026-09-14',
            tipo_seguimiento='Presencial Aula',
            observaciones='Observaciones de la visita.',
            compromisos='Compromiso institucional.',
            fecha_verificacion='2026-10-01',
        )
        self.client.force_login(self.instructor)

        response = self.client.get(f'/seguimiento/{bitacora.pk}/acta-pdf/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))
        self.assertIn(b'ReportLab PDF Library', response.content)

    def test_guardar_bitacora_con_firmas_canvas(self):
        firma_png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
        self.client.force_login(self.instructor)

        response = self.client.post('/seguimiento/nuevo/', {
            'ficha': self.ficha.pk,
            'matricula': '',
            'fecha_visita': '2026-09-15',
            'tipo_seguimiento': 'Presencial Aula',
            'observaciones': 'Visita con firmas digitales.',
            'compromisos': '',
            'fecha_verificacion': '',
            'firma_instructor': firma_png,
            'firma_docente_enlace': firma_png,
            'latitud_gps': '11.240800',
            'longitud_gps': '-74.199000',
            'precision_gps': '8.50',
        })

        self.assertEqual(response.status_code, 302)
        bitacora = BitacoraSeguimiento.objects.latest('id')
        self.assertTrue(bitacora.firma_instructor.name)
        self.assertTrue(bitacora.firma_docente_enlace.name)
        self.assertEqual(str(bitacora.latitud), '11.240800')
        self.assertEqual(str(bitacora.longitud), '-74.199000')
        self.assertEqual(str(bitacora.precision_gps), '8.50')

        detalle = self.client.get(f'/seguimiento/{bitacora.pk}/')
        self.assertContains(detalle, 'Ubicación verificada de la visita')
        self.assertContains(detalle, 'Abrir en Google Maps')

    def test_control_asistencia_guarda_y_actualiza_estados(self):
        aprendiz_uno = User.objects.create_user(username='aprendiz_uno', first_name='Ana', last_name='Uno')
        aprendiz_dos = User.objects.create_user(username='aprendiz_dos', first_name='Luis', last_name='Dos')
        matricula_uno = Matricula.objects.create(ficha=self.ficha, aprendiz=aprendiz_uno, grado_escolar='10')
        matricula_dos = Matricula.objects.create(ficha=self.ficha, aprendiz=aprendiz_dos, grado_escolar='11')
        self.client.force_login(self.instructor)
        url = f'/seguimiento/asistencia/?ficha={self.ficha.pk}&fecha=2026-09-15'

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Control de Asistencia Diaria')

        response = self.client.post(url, {
            f'asistencia_{matricula_uno.pk}': 'A',
            f'asistencia_{matricula_dos.pk}': 'J',
        })
        self.assertRedirects(response, url)
        self.assertEqual(
            AsistenciaAprendiz.objects.get(matricula=matricula_uno, fecha='2026-09-15').estado,
            'A',
        )
        self.assertEqual(
            AsistenciaAprendiz.objects.get(matricula=matricula_dos, fecha='2026-09-15').estado,
            'J',
        )

        self.client.post(url, {f'asistencia_{matricula_uno.pk}': 'P', f'asistencia_{matricula_dos.pk}': 'P'})
        self.assertEqual(AsistenciaAprendiz.objects.filter(fecha='2026-09-15').count(), 2)
        self.assertEqual(AsistenciaAprendiz.objects.get(matricula=matricula_uno, fecha='2026-09-15').estado, 'P')
