from django.db import models


class Transaccion(models.Model):
    ESTADO_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('cancelled', 'Cancelado'),
        ('in_process', 'En proceso'),
    ]

    negocio = models.ForeignKey(
        'tenants.Negocio',
        on_delete=models.CASCADE,
        related_name='transacciones'
    )
    preference_id = models.CharField(max_length=200, unique=True, db_index=True, blank=True, null=True)
    payment_id = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    external_reference = models.CharField(max_length=200, blank=True, null=True, db_index=True)

    amount = models.FloatField()
    description = models.CharField(max_length=500, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)

    status = models.CharField(max_length=50, choices=ESTADO_CHOICES, default='pending')
    init_point = models.TextField(blank=True, null=True)
    metadata_json = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.negocio} | {self.external_reference} | {self.status}"

    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-created_at']
