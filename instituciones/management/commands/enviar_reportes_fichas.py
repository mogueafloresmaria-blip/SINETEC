from collections import defaultdict

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.urls import reverse

from academico.models import Ficha
from evaluaciones.models import JuicioEvaluativo


class Command(BaseCommand):
    help = 'Envía un resumen periódico de avance de fichas a rectoría y docente enlace.'

    def handle(self, *args, **options):
        enviados = 0
        omitidos = 0
        fichas = Ficha.objects.filter(
            estado='En Ejecucion',
            institucion__activa=True,
        ).select_related('institucion', 'programa').annotate(
            total_aprendices=Count('matriculas', distinct=True),
            total_juicios=Count('matriculas__juicios_evaluativos', distinct=True),
            aprobados=Count('matriculas__juicios_evaluativos', filter=Q(matriculas__juicios_evaluativos__juicio_valor='A'), distinct=True),
            no_aprobados=Count('matriculas__juicios_evaluativos', filter=Q(matriculas__juicios_evaluativos__juicio_valor='D'), distinct=True),
        )
        agrupadas = defaultdict(list)
        for ficha in fichas:
            destinatarios = [
                correo for correo in (ficha.institucion.rector_email, ficha.institucion.enlace_email)
                if correo
            ]
            if not destinatarios:
                omitidos += 1
                continue
            agrupadas[tuple(sorted(set(destinatarios)))].append(ficha)

        for destinatarios, fichas_destino in agrupadas.items():
            institucion = fichas_destino[0].institucion
            lineas = [
                f'Reporte de avance de fichas - {institucion.nombre}',
                f'Municipio: {institucion.municipio}',
                '',
            ]
            for ficha in fichas_destino:
                porcentaje = round(ficha.aprobados / ficha.total_juicios * 100, 1) if ficha.total_juicios else 0
                lineas.extend([
                    f'Ficha {ficha.codigo_ficha} - {ficha.programa.denominacion}',
                    f'Aprendices: {ficha.total_aprendices}',
                    f'Juicios registrados: {ficha.total_juicios}',
                    f'Aprobados: {ficha.aprobados} | No aprobados: {ficha.no_aprobados}',
                    f'Porcentaje de aprobación: {porcentaje}%',
                    '',
                ])
            cuerpo = '\n'.join(lineas)
            mensaje = EmailMultiAlternatives(
                subject=f'SINETEC | Avance académico - {institucion.nombre}',
                body=cuerpo,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'sinetec@localhost'),
                to=list(destinatarios),
            )
            mensaje.send(fail_silently=False)
            enviados += len(destinatarios)

        self.stdout.write(self.style.SUCCESS(
            f'Reporte enviado a {enviados} destinatarios; {omitidos} fichas omitidas sin correos configurados.'
        ))
