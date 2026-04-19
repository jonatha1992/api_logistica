from django.db import migrations
from apps.tenants.fields import EncryptedField


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0003_negocio_brand_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='negocio',
            name='resend_api_key',
            field=EncryptedField(
                blank=True, null=True, verbose_name='API Key de Resend',
                help_text='API Key de resend.com para envío de emails. Se encripta automáticamente.'
            ),
        ),
    ]
