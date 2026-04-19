from django.db import models


class PlantillaEmail(models.Model):
    negocio = models.ForeignKey(
        'tenants.Negocio',
        on_delete=models.CASCADE,
        related_name='plantillas'
    )
    slug = models.SlugField(max_length=100,
                            help_text='Identificador único. Ej: recupero-clave, pago-confirmado')
    asunto = models.CharField(max_length=500,
                              help_text='Soporte de variables Jinja2: {{ nombre }}, {{ link }}')
    cuerpo_html = models.TextField(
        help_text='HTML completo del email. Soporta variables Jinja2: {{ variable }}'
    )
    activa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.negocio} | {self.slug}"

    class Meta:
        verbose_name = 'Plantilla de Email'
        verbose_name_plural = 'Plantillas de Email'
        unique_together = [['negocio', 'slug']]
        ordering = ['negocio', 'slug']
