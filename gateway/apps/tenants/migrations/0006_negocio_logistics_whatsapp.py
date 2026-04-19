from django.db import migrations, models
import apps.tenants.fields


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0005_alter_negocio_texto_footer'),
    ]

    operations = [
        migrations.AddField(
            model_name='negocio',
            name='envia_token',
            field=apps.tenants.fields.EncryptedField(blank=True, null=True, verbose_name='Token Envia.com', help_text='Token de API de Envia.com para crear envíos.'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='envia_ambiente',
            field=models.CharField(
                max_length=4,
                choices=[('TEST', 'Testing'), ('PRO', 'Producción')],
                default='TEST',
                verbose_name='Ambiente Envia.com',
            ),
        ),
        migrations.AddField(
            model_name='negocio',
            name='whatsapp_provider',
            field=models.CharField(blank=True, null=True, max_length=50, verbose_name='Proveedor WhatsApp', help_text='Ej: twilio, wati, 360dialog, meta'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='whatsapp_api_key',
            field=apps.tenants.fields.EncryptedField(blank=True, null=True, verbose_name='API Key WhatsApp'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='whatsapp_number',
            field=models.CharField(blank=True, null=True, max_length=30, verbose_name='Número WhatsApp', help_text='Número en formato internacional. Ej: +5491122334455'),
        ),
    ]
