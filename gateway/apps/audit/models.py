from django.db import models


class AuditLog(models.Model):
    negocio = models.ForeignKey(
        'tenants.Negocio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.endpoint} → {self.status_code} ({self.created_at:%Y-%m-%d %H:%M})"

    class Meta:
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-created_at']
