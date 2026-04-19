from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0002_negocio_color_primario_negocio_color_secundario_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='negocio',
            name='nombre_comercial',
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name='Nombre comercial',
                help_text='Nombre mostrado en emails y templates. Si está vacío, usa el campo "Nombre".'
            ),
        ),
        migrations.AddField(
            model_name='negocio',
            name='slogan',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Slogan / descripción corta'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='icono_emoji',
            field=models.CharField(
                default='📦', max_length=10, verbose_name='Ícono del negocio',
                help_text='Emoji o símbolo para el encabezado de emails. Ej: 📦 🚀 🛒 ✈️'
            ),
        ),
        migrations.AddField(
            model_name='negocio',
            name='email_soporte',
            field=models.EmailField(blank=True, null=True, verbose_name='Email de soporte'),
        ),
        migrations.AddField(
            model_name='negocio',
            name='texto_footer',
            field=models.CharField(
                blank=True, max_length=500, null=True, verbose_name='Texto del pie de email',
                help_text='Texto personalizado en el footer de todos los emails.'
            ),
        ),
        migrations.AlterField(
            model_name='negocio',
            name='color_primario',
            field=models.CharField(default='#4f46e5', max_length=7, verbose_name='Color primario (hex)'),
        ),
        migrations.AlterField(
            model_name='negocio',
            name='color_secundario',
            field=models.CharField(default='#7c3aed', max_length=7, verbose_name='Color secundario (hex)'),
        ),
    ]
