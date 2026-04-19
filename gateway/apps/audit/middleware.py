from .models import AuditLog


class AuditLogMiddleware:
    """
    Registra cada interacción autenticada en AuditLog.
    Permite debugear si un correo o pago falló en un negocio específico.
    Ejecuta DESPUÉS de la respuesta para capturar el status_code real.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        negocio = getattr(request, 'negocio', None)
        if negocio is not None:
            try:
                AuditLog.objects.create(
                    negocio=negocio,
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                )
            except Exception:
                pass  # El log no debe interrumpir la respuesta

        return response
