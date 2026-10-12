from django.db import migrations, models

# Valores azules por defecto antiguos que nunca se aplicaron a la interfaz.
ANTIGUOS = {
    'color_primario': '#0F2942',
    'color_secundario': '#3B82F6',
    'color_acento': '#EEF2FF',
}
NUEVOS = {
    'color_primario': '#8B5E3C',
    'color_secundario': '#5A3825',
    'color_acento': '#EFEBE4',
}


def migrar_colores_antiguos(apps, schema_editor):
    """Si el colegio conserva los azules sin uso, pasa a la paleta vigente de EDUNOVA."""
    ConfiguracionColegio = apps.get_model('usuarios', 'ConfiguracionColegio')
    for cfg in ConfiguracionColegio.objects.all():
        for campo, antiguo in ANTIGUOS.items():
            if (getattr(cfg, campo) or '').upper() == antiguo.upper():
                setattr(cfg, campo, NUEVOS[campo])
        cfg.save()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0017_papelerareciclaje_modulo_origen_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='configuracioncolegio',
            name='color_fondo',
            field=models.CharField(default='#F8F6F0', max_length=20, verbose_name='Color de Fondo'),
        ),
        migrations.AddField(
            model_name='configuracioncolegio',
            name='color_texto',
            field=models.CharField(default='#2D231E', max_length=20, verbose_name='Color de Texto'),
        ),
        migrations.AlterField(
            model_name='configuracioncolegio',
            name='color_primario',
            field=models.CharField(default='#8B5E3C', max_length=20, verbose_name='Color Principal'),
        ),
        migrations.AlterField(
            model_name='configuracioncolegio',
            name='color_secundario',
            field=models.CharField(default='#5A3825', max_length=20, verbose_name='Color Secundario'),
        ),
        migrations.AlterField(
            model_name='configuracioncolegio',
            name='color_acento',
            field=models.CharField(default='#EFEBE4', max_length=20, verbose_name='Color de Acento'),
        ),
        migrations.RunPython(migrar_colores_antiguos, migrations.RunPython.noop),
    ]
