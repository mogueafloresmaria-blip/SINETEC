from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from academico.models import (
    CargaAcademica,
    Competencia,
    Ficha,
    HorarioFicha,
    Matricula,
    ProgramaFormacion,
    ResultadoAprendizaje,
)
from evaluaciones.models import JuicioEvaluativo
from instituciones.models import InstitucionEducativa
from seguimiento.models import AsistenciaAprendiz
from usuarios.models import ConfiguracionColegio, FamiliaAcudiente, PagoPension, PerfilUsuario, Rol, TransporteRuta


class Command(BaseCommand):
    help = 'Puebla el sistema con datos escolares demo coherentes e idempotentes.'

    @transaction.atomic
    def handle(self, *args, **options):
        hoy = date.today()
        roles = self._roles()
        self._configuracion()
        instituciones = self._instituciones()
        docentes = self._docentes(roles['Docente I.E.'])
        programas = self._programas(instituciones)
        fichas = self._fichas(programas, instituciones, docentes)
        self._carga_academica(programas, docentes)
        alumnos = self._alumnos(roles['Estudiante'], fichas)
        self._acudientes(alumnos)
        self._horarios(fichas, programas, docentes)
        self._calificaciones(alumnos, programas, docentes, hoy)
        self._asistencia(alumnos, docentes, hoy)
        self._pagos(alumnos)
        self._rutas()

        self.stdout.write(self.style.SUCCESS(
            f'Datos escolares listos: {len(instituciones)} colegios, {len(programas)} cursos, '
            f'{len(docentes)} profesores y {len(alumnos)} alumnos.'
        ))

    def _roles(self):
        nombres = {
            'Administrador': 'Administración general',
            'Coordinador': 'Coordinación académica',
            'Docente I.E.': 'Docente de la institución educativa',
            'Estudiante': 'Alumno matriculado',
        }
        return {
            nombre: Rol.objects.get_or_create(nombre=nombre, defaults={'descripcion': descripcion})[0]
            for nombre, descripcion in nombres.items()
        }

    def _configuracion(self):
        colegio = ConfiguracionColegio.get_solo()
        colegio.nombre = 'Institución Educativa Distrital Nuevo Horizonte'
        colegio.lema = 'Educación, convivencia y futuro'
        colegio.codigo_dane = '147001000234'
        colegio.nit = '900.456.789-1'
        colegio.direccion = 'Carrera 12 # 18-40, Santa Marta'
        colegio.telefono = '+57 605 421 9988'
        colegio.email = 'contacto@nuevahorizonte.edu.co'
        colegio.save()

    def _instituciones(self):
        datos = [
            ('147001000234', 'I.E.D. Nuevo Horizonte', 'Santa Marta'),
            ('147189000567', 'I.E. Departamental La Esperanza', 'Ciénaga'),
            ('147053000890', 'I.E. Rural Sierra Verde', 'Aracataca'),
        ]
        instituciones = []
        for codigo, nombre, municipio in datos:
            institucion, _ = InstitucionEducativa.objects.get_or_create(
                codigo_dane=codigo,
                defaults={
                    'nombre': nombre,
                    'municipio': municipio,
                    'direccion': 'Carrera Principal # 10-20',
                    'telefono': '+57 300 555 0100',
                    'rector_nombre': 'María Fernanda Gómez',
                    'activa': True,
                },
            )
            instituciones.append(institucion)
        return instituciones

    def _docentes(self, rol):
        nombres = [
            ('Laura', 'Martínez Rojas', 'Matemáticas'),
            ('Carlos', 'Mendoza Pérez', 'Lengua Castellana'),
            ('Patricia', 'Vargas Cotes', 'Ciencias Naturales'),
            ('Andrés', 'Torres Díaz', 'Ciencias Sociales'),
            ('Diana', 'Herrera López', 'Inglés'),
            ('Jorge', 'Ramírez Silva', 'Educación Física'),
            ('Sofía', 'Morales Castro', 'Artística'),
            ('Felipe', 'Gómez Ruiz', 'Tecnología'),
            ('Natalia', 'Pardo León', 'Ética y Valores'),
            ('Miguel', 'Suárez Peña', 'Matemáticas'),
            ('Valentina', 'Ríos Gómez', 'Lengua Castellana'),
            ('Ricardo', 'Navarro Díaz', 'Ciencias Naturales'),
            ('Camila', 'Ortega Salas', 'Inglés'),
            ('Daniel', 'Fuentes Mora', 'Ciencias Sociales'),
            ('Adriana', 'Castro Mejía', 'Orientación Escolar'),
        ]
        docentes = []
        for indice, (nombre, apellido, especialidad) in enumerate(nombres, start=1):
            username = f'docente_colegio_{indice:02d}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': nombre,
                    'last_name': apellido,
                    'email': f'{username}@nuevahorizonte.edu.co',
                },
            )
            if created:
                user.set_password('Colegio2026*')
                user.save(update_fields=['password'])
            perfil = user.perfil
            perfil.rol = rol
            perfil.tipo_documento = 'CC'
            perfil.numero_documento = f'100200{indice:04d}'
            perfil.telefono = f'300555{indice:04d}'
            perfil.genero = 'Femenino' if nombre in {'Laura', 'Patricia', 'Diana', 'Sofía', 'Natalia', 'Valentina', 'Camila', 'Adriana'} else 'Masculino'
            perfil.save()
            docentes.append((user, especialidad))
        return docentes

    def _programas(self, instituciones):
        datos = [
            ('COL-MAT-01', 'Matemáticas'),
            ('COL-LEN-01', 'Lengua Castellana'),
            ('COL-CIE-01', 'Ciencias Naturales'),
            ('COL-SOC-01', 'Ciencias Sociales'),
        ]
        programas = []
        for indice, (codigo, nombre) in enumerate(datos):
            programa, _ = ProgramaFormacion.objects.get_or_create(
                codigo_programa=codigo,
                defaults={
                    'denominacion': nombre,
                    'tipo_programa': 'Otro',
                    'duracion_meses': 10,
                    'duracion_horas': 120,
                    'institucion': instituciones[indice % len(instituciones)],
                    'fecha_inicio': date(hoy_year(), 1, 15),
                    'fecha_fin': date(hoy_year(), 11, 30),
                    'activo': True,
                },
            )
            competencia, _ = Competencia.objects.get_or_create(
                programa=programa,
                codigo=f'COMP-{codigo[-3:]}',
                defaults={'descripcion': f'Competencias escolares de {nombre}.'},
            )
            ResultadoAprendizaje.objects.get_or_create(
                competencia=competencia,
                codigo=f'RA-{codigo[-3:]}',
                defaults={'descripcion': f'Desarrolla aprendizajes fundamentales en {nombre}.'},
            )
            programas.append(programa)
        return programas

    def _fichas(self, programas, instituciones, docentes):
        fichas = []
        for indice in range(3):
            ficha, _ = Ficha.objects.get_or_create(
                codigo_ficha=f'COL-2026-{indice + 1:03d}',
                defaults={
                    'programa': programas[indice],
                    'institucion': instituciones[indice],
                    'instructor_lider': docentes[indice][0],
                    'fecha_inicio': date(hoy_year(), 1, 15),
                    'fecha_fin': date(hoy_year(), 11, 30),
                    'estado': 'En Ejecucion',
                },
            )
            fichas.append(ficha)
        return fichas

    def _alumnos(self, rol, fichas):
        nombres = [
            ('Ana', 'Rodríguez Pérez'), ('Luis', 'Fernández Gómez'), ('Mariana', 'Castro Ruiz'),
            ('Juan', 'Pérez López'), ('Sofía', 'Martínez Díaz'), ('Mateo', 'García Torres'),
            ('Valeria', 'Hernández Silva'), ('Samuel', 'Rojas Castro'), ('Isabella', 'Moreno Vargas'),
            ('Nicolás', 'Suárez Gómez'), ('Gabriela', 'Mendoza León'), ('Sebastián', 'Díaz Pardo'),
            ('Salomé', 'Vega Ríos'), ('David', 'Cárdenas Mora'), ('Manuela', 'Pineda Ruiz'),
            ('Tomás', 'Navarro Gil'), ('Luciana', 'Santos Pérez'), ('Emiliano', 'Quintero Díaz'),
            ('Sara', 'Mejía Torres'), ('Martín', 'Fuentes Castro'), ('Emma', 'Peña Silva'),
            ('Alejandro', 'Bermúdez Rojas'), ('Antonella', 'Mora Gómez'), ('Santiago', 'León Vargas'),
            ('Laura', 'Salas Herrera'), ('Nicolás', 'Rincón Pérez'), ('Juliana', 'Ospina Díaz'),
            ('Daniel', 'Cruz Moreno'), ('Paula', 'Reyes Castro'), ('Miguel', 'Vargas López'),
            ('Elena', 'Gómez Pardo'), ('Carlos', 'Torres Ruiz'), ('María', 'Ríos Silva'),
            ('Andrés', 'Molina Gómez'), ('Carolina', 'Duarte Pérez'), ('Felipe', 'Sierra Díaz'),
            ('Natalia', 'López Mora'), ('Joaquín', 'Parra Torres'), ('Renata', 'Cano Ruiz'),
            ('Diego', 'Vega Castro'), ('Isabel', 'Márquez León'), ('Gabriel', 'Soto Ríos'),
            ('Mía', 'Herrera Gómez'), ('Bruno', 'Pérez Vargas'), ('Alicia', 'Naranjo Díaz'),
            ('Esteban', 'Rojas Silva'), ('Clara', 'Mendoza Pérez'), ('Martina', 'Castro López'),
            ('Simón', 'García Ríos'), ('Victoria', 'Pardo Torres'), ('Samuel', 'Ruiz Moreno'),
        ]
        alumnos = []
        for indice, (nombre, apellido) in enumerate(nombres, start=1):
            documento = f'110300{indice:04d}'
            username = f'alumno_colegio_{indice:02d}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': nombre,
                    'last_name': apellido,
                    'email': f'{username}@nuevahorizonte.edu.co',
                },
            )
            if created:
                user.set_password('Colegio2026*')
                user.save(update_fields=['password'])
            perfil = user.perfil
            perfil.rol = rol
            perfil.tipo_documento = 'TI'
            perfil.numero_documento = documento
            perfil.telefono = f'301555{indice:04d}'
            perfil.save()
            ficha = fichas[(indice - 1) % len(fichas)]
            grado = '10' if indice % 2 else '11'
            matricula, _ = Matricula.objects.get_or_create(
                ficha=ficha,
                aprendiz=user,
                defaults={
                    'grado_escolar': grado,
                    'seccion': 'A' if indice % 3 else 'B',
                    'acudiente_nombre': f'Acudiente de {nombre}',
                    'acudiente_telefono': f'302555{indice:04d}',
                },
            )
            alumnos.append((user, matricula))
        return alumnos

    def _acudientes(self, alumnos):
        for indice in range(0, len(alumnos), 2):
            user = alumnos[indice][0]
            familia, _ = FamiliaAcudiente.objects.get_or_create(
                documento=f'ACU-{indice + 1:04d}',
                defaults={
                    'nombre_acudiente': f'Acudiente de {user.get_full_name()}',
                    'parentesco': 'Madre' if indice % 4 else 'Padre',
                    'telefono': f'302555{indice + 1:04d}',
                    'email': f'acudiente{indice + 1:02d}@correo.com',
                    'direccion': 'Carrera 10 # 20-30',
                },
            )
            familia.estudiantes.add(user)

    def _carga_academica(self, programas, docentes):
        for indice, (docente, _) in enumerate(docentes):
            CargaAcademica.objects.get_or_create(
                profesor=docente,
                programa=programas[indice % len(programas)],
                nivel='Secundaria' if indice % 2 else 'Primaria',
                grado='1er Año' if indice % 2 else '5to Grado',
                seccion='A',
                anio_lectivo=hoy_year(),
            )

    def _horarios(self, fichas, programas, docentes):
        bloques = [('1', time(7, 0), time(8, 0)), ('1', time(8, 0), time(9, 0)), ('2', time(7, 0), time(8, 0)), ('3', time(9, 0), time(10, 0))]
        for indice, (dia, inicio, fin) in enumerate(bloques):
            HorarioFicha.objects.get_or_create(
                ficha=fichas[indice % len(fichas)],
                dia=dia,
                hora_inicio=inicio,
                defaults={
                    'hora_fin': fin,
                    'instructor': docentes[indice % len(docentes)][0],
                    'programa': programas[indice % len(programas)],
                    'nivel': 'Secundaria',
                    'grado': '1er Año',
                    'seccion': 'A',
                    'ambiente': f'Aula {101 + indice}',
                    'tema': programas[indice % len(programas)].denominacion,
                },
            )

    def _calificaciones(self, alumnos, programas, docentes, hoy):
        for indice, (_, matricula) in enumerate(alumnos[:20]):
            competencia = programas[indice % len(programas)].competencias.first()
            rap = competencia.resultados.first()
            JuicioEvaluativo.objects.get_or_create(
                matricula=matricula,
                resultado_aprendizaje=rap,
                defaults={
                    'instructor': docentes[indice % len(docentes)][0],
                    'juicio_valor': 'A' if indice % 5 else 'D',
                    'fecha_evaluacion': hoy - timedelta(days=indice % 30),
                    'observaciones': 'Registro demo de evaluación escolar.',
                },
            )

    def _asistencia(self, alumnos, docentes, hoy):
        for indice, (_, matricula) in enumerate(alumnos[:30]):
            for dias in (1, 2, 3):
                AsistenciaAprendiz.objects.get_or_create(
                    matricula=matricula,
                    fecha=hoy - timedelta(days=dias),
                    defaults={
                        'estado': 'A' if indice % 11 == 0 else 'P',
                        'registrado_por': docentes[indice % len(docentes)][0],
                        'observaciones': 'Registro escolar demo.',
                    },
                )

    def _pagos(self, alumnos):
        for indice, (user, _) in enumerate(alumnos[:12], start=1):
            PagoPension.objects.get_or_create(
                estudiante=user,
                concepto='Pensión escolar marzo',
                defaults={
                    'monto': Decimal('185000.00'),
                    'metodo_pago': 'Efectivo' if indice % 2 else 'Transferencia',
                },
            )

    def _rutas(self):
        rutas = [
            ('Ruta Centro', 'Carlos Mendoza', 'COL-101', 28, '180000.00'),
            ('Ruta Norte', 'Patricia Vargas', 'COL-202', 35, '220000.00'),
            ('Ruta Rural', 'Hernán Gutiérrez', 'COL-303', 22, '150000.00'),
        ]
        for nombre, conductor, placa, capacidad, costo in rutas:
            TransporteRuta.objects.get_or_create(
                placa=placa,
                defaults={'nombre': nombre, 'conductor': conductor, 'capacidad': capacidad, 'costo_mensual': costo},
            )


def hoy_year():
    return date.today().year
