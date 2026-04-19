import uuid
from django.db import models
from .fields import EncryptedField


class Negocio(models.Model):
    nombre = models.CharField(max_length=200)
    api_key = models.CharField(max_length=64, unique=True, db_index=True, editable=False)

    # Mercado Pago (encriptado)
    mp_access_token = EncryptedField(blank=True, null=True, verbose_name='Token Mercado Pago')
    webhook_notificacion = models.URLField(max_length=500, blank=True, null=True,
                                           verbose_name='URL Webhook de notificación')

    # Datos de empresa
    razon_social = models.CharField(max_length=300, blank=True, null=True, verbose_name='Razón social')
    cuit = models.CharField(max_length=20, blank=True, null=True, verbose_name='CUIT')
    telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=500, blank=True, null=True, verbose_name='Dirección')
    sitio_web = models.URLField(max_length=300, blank=True, null=True, verbose_name='Sitio web')

    # Identidad de marca (para templates genéricos)
    nombre_comercial = models.CharField(
        max_length=200, blank=True, null=True, verbose_name='Nombre comercial',
        help_text='Nombre mostrado en emails y templates. Si está vacío, usa el campo "Nombre".'
    )
    slogan = models.CharField(max_length=300, blank=True, null=True, verbose_name='Slogan / descripción corta')
    icono_emoji = models.CharField(
        max_length=10, default='📦', verbose_name='Ícono del negocio',
        help_text='Emoji o símbolo para el encabezado de emails. Ej: 📦 🚀 🛒 ✈️'
    )
    email_soporte = models.EmailField(blank=True, null=True, verbose_name='Email de soporte')
    texto_footer = models.CharField(
        max_length=500, blank=True, null=True, verbose_name='Texto del pie de email',
        help_text='Texto personalizado en el footer de todos los emails. Ej: "Líder en logística del norte"'
    )

    # Proveedores de email y pagos (encriptados)
    resend_api_key = EncryptedField(blank=True, null=True, verbose_name='API Key de Resend',
                                    help_text='API Key de resend.com para envío de emails. Se encripta automáticamente.')

    # Branding
    logo_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='URL del logo')
    color_primario = models.CharField(max_length=7, default='#4f46e5', verbose_name='Color primario (hex)')
    color_secundario = models.CharField(max_length=7, default='#7c3aed', verbose_name='Color secundario (hex)')

    # SMTP (contraseña encriptada)
    smtp_host = models.CharField(max_length=200, blank=True, null=True, verbose_name='Servidor SMTP')
    smtp_port = models.IntegerField(default=587, verbose_name='Puerto SMTP')
    smtp_user = models.CharField(max_length=200, blank=True, null=True, verbose_name='Usuario SMTP')
    smtp_pass = EncryptedField(blank=True, null=True, verbose_name='Contraseña SMTP')
    smtp_from = models.EmailField(blank=True, null=True, verbose_name='Email remitente')

    # Logística - Envia.com (token encriptado)
    envia_token = EncryptedField(blank=True, null=True, verbose_name='Token Envia.com',
                                 help_text='Token de API de Envia.com para crear envíos.')
    envia_ambiente = models.CharField(
        max_length=4, choices=[('TEST', 'Testing'), ('PRO', 'Producción')],
        default='TEST', verbose_name='Ambiente Envia.com'
    )

    # WhatsApp
    whatsapp_provider = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='Proveedor WhatsApp',
        help_text='Ej: twilio, wati, 360dialog, meta'
    )
    whatsapp_api_key = EncryptedField(blank=True, null=True, verbose_name='API Key WhatsApp')
    whatsapp_number = models.CharField(
        max_length=30, blank=True, null=True, verbose_name='Número WhatsApp',
        help_text='Número en formato internacional. Ej: +5491122334455'
    )

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Negocio'
        verbose_name_plural = 'Negocios'
        ordering = ['-created_at']
