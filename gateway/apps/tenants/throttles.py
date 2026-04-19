from rest_framework.throttling import SimpleRateThrottle


class PerNegocioThrottle(SimpleRateThrottle):
    """
    Rate limit por negocio (no por IP).
    Evita que un negocio sature el sistema de correos afectando a los demás.
    Límite: 30 emails/minuto por negocio.
    """
    rate = '30/minute'
    scope = 'negocio_email'

    def get_cache_key(self, request, view):
        negocio = getattr(request, 'negocio', None)
        if negocio:
            return f'throttle_negocio_{negocio.id}'
        return self.get_ident(request)
