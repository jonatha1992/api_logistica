from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0006_negocio_logistics_whatsapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='negocio',
            name='usa_email',
            field=models.BooleanField(default=False, verbose_name='Usa Email'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='usa_logistica',
            field=models.BooleanField(default=False, verbose_name='Usa Logística'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='usa_pagos',
            field=models.BooleanField(default=False, verbose_name='Usa Pagos'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='usa_whatsapp',
            field=models.BooleanField(default=False, verbose_name='Usa WhatsApp'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='email_principal',
            field=models.EmailField(blank=True, null=True, verbose_name='Email principal'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='logo_file',
            field=models.ImageField(blank=True, null=True, upload_to='logos/', verbose_name='Logo (archivo)'),
        ),
    ]
