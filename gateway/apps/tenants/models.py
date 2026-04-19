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

    # SMTP (contraseña encriptada)
    smtp_host = models.CharField(max_length=200, blank=True, null=True, verbose_name='Servidor SMTP')
    smtp_port = models.IntegerField(default=587, verbose_name='Puerto SMTP')
    smtp_user = models.CharField(max_length=200, blank=True, null=True, verbose_name='Usuario SMTP')
    smtp_pass = EncryptedField(blank=True, null=True, verbose_name='Contraseña SMTP')
    smtp_from = models.EmailField(blank=True, null=True, verbose_name='Email remitente')

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
