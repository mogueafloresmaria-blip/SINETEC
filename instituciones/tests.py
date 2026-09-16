from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.contrib.auth.models import User

from academico.models import Ficha, Matricula, ProgramaFormacion
from instituciones.models import InstitucionEducativa



@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ReporteFichasCommandTest(TestCase):
	def test_comando_envia_reporte_a_contactos_institucionales(self):
		institucion = InstitucionEducativa.objects.create(
			codigo_dane='147001001111',
			nombre='Colegio Reporte',
			municipio='Santa Marta',
			rector_email='rector@example.com',
			enlace_email='enlace@example.com',
		)
		programa = ProgramaFormacion.objects.create(
			codigo_programa='REPORT-01', denominacion='Programa de Reporte'
		)
		instructor = User.objects.create_user(username='instructor_reporte')
		ficha = Ficha.objects.create(
			codigo_ficha='REPORT-2501', programa=programa, institucion=institucion,
			instructor_lider=instructor, fecha_inicio='2026-02-01', fecha_fin='2026-11-30',
		)
		aprendiz = User.objects.create_user(username='aprendiz_reporte')
		Matricula.objects.create(ficha=ficha, aprendiz=aprendiz, grado_escolar='10')

		call_command('enviar_reportes_fichas')

		self.assertEqual(len(mail.outbox), 1)
		self.assertCountEqual(mail.outbox[0].to, ['rector@example.com', 'enlace@example.com'])
		self.assertIn('REPORT-2501', mail.outbox[0].body)
