"""
Aplicación: evaluaciones
Modelo: JuicioEvaluativo
Reglas de Negocio Asociadas: RN-003 (Juicio Oficial 'A' y 'D'), RN-004 (Inmutabilidad por Cierre de Periodo)
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from academico.models import Matricula, ResultadoAprendizaje


class JuicioEvaluativo(models.Model):
    """
    Registro oficial del juicio cualitativo asignado por el instructor SENA
    a cada resultado de aprendizaje cursado por el aprendiz de Media Técnica.
    """
    # RN-003: Escala cualitativa oficial del SENA
    JUICIOS_CHOICES = [
        ('A', 'A - Aprobado (Alcanzó los criterios de desempeño)'),
        ('D', 'D - No Aprobado (Requiere plan de mejoramiento / No alcanzado)'),
    ]

    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='juicios_evaluativos',
        verbose_name="Aprendiz Matriculado"
    )
    resultado_aprendizaje = models.ForeignKey(
        ResultadoAprendizaje,
        on_delete=models.PROTECT,
        related_name='juicios_emitidos',
        verbose_name="Resultado de Aprendizaje (RAP)"
    )
    instructor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='juicios_asentados',
        verbose_name="Instructor Evaluador"
    )
    juicio_valor = models.CharField(
        max_length=1,
        choices=JUICIOS_CHOICES,
        verbose_name="Juicio de Valor Cualitativo"
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name="Retroalimentación Pedagógica",
        help_text="Recomendado especialmente cuando el juicio es 'D' (No Aprobado)."
    )
    fecha_evaluacion = models.DateField(
        verbose_name="Fecha de la Evaluación"
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Marca de Tiempo del Registro (Auditoría)"
    )

    class Meta:
        verbose_name = "Juicio Evaluativo"
        verbose_name_plural = "Juicios Evaluativos"
        # Un aprendiz solo tiene una calificación final por cada resultado de aprendizaje
        unique_together = ('matricula', 'resultado_aprendizaje')
        ordering = ['matricula', 'resultado_aprendizaje__codigo']

    def __str__(self):
        nombre_aprendiz = self.matricula.aprendiz.get_full_name() or self.matricula.aprendiz.username
        return f"{nombre_aprendiz} - {self.resultado_aprendizaje.codigo}: Juicio '{self.juicio_valor}'"

    def clean(self):
        """
        Validación de las reglas de negocio institucionales:
        1. RN-004: No permitir crear o modificar juicios si la ficha tiene su periodo formalmente cerrado.
        2. RN-003: Validar que el juicio pertenezca a la escala oficial ('A' o 'D').
        """
        super().clean()
        
        # Validar regla RN-004
        if hasattr(self, 'matricula') and self.matricula and self.matricula.ficha.periodo_cerrado:
            raise ValidationError(
                "Operación Denegada (RN-004): El periodo evaluativo de esta ficha técnica se encuentra "
                "formalmente cerrado por la Coordinación. No se permiten nuevas calificaciones ni modificaciones."
            )

        # Validar regla RN-003
        if self.juicio_valor not in ['A', 'D']:
            raise ValidationError({
                'juicio_valor': "El juicio asignado debe ser exclusivamente 'A' (Aprobado) o 'D' (No Aprobado) (RN-003)."
            })
