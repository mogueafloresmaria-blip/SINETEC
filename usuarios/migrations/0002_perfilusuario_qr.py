import uuid

from django.db import migrations, models


def asignar_tokens_qr(apps, schema_editor):
    PerfilUsuario = apps.get_model('usuarios', 'PerfilUsuario')
    for perfil in PerfilUsuario.objects.filter(qr_token__isnull=True):
        perfil.qr_token = uuid.uuid4()
        perfil.save(update_fields=['qr_token'])


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilusuario',
            name='qr_token',
            field=models.UUIDField(editable=False, null=True, verbose_name='Token del carnet QR'),
        ),
        migrations.RunPython(asignar_tokens_qr, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='perfilusuario',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='Token del carnet QR'),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='carnets_qr/%Y/%m/', verbose_name='Código QR del carnet'),
        ),
    ]
