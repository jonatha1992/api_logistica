from django.http import JsonResponse
from .models import Negocio


class TenantMiddleware:
    """
    Intercepta cada request, busca el Negocio por API key e inyecta
    request.negocio para que las views puedan usarlo directamente.
    """
    RUTAS_PUBLICAS = {
        '/',
        '/api/v1/status',
        '/api/v1/config',
    }
    PREFIJOS_PUBLICOS = (
        '/admin/',
        '/panel/',
        '/docs',
        '/redoc',
        '/api/schema/',
        '/api/v1/webhooks/mercadopago/',
        '/api/v1/carriers',
        '/api/v1/cotizar',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.negocio = None

        if self._es_publica(request.path):
            return self.get_response(request)

        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return JsonResponse(
                {'detail': 'Header requerido: Authorization: Bearer <API_KEY_DEL_NEGOCIO>'},
                status=401
            )

        api_key = auth.removeprefix('Bearer ').strip()

        try:
            request.negocio = Negocio.objects.get(api_key=api_key, activo=True)
        except Negocio.DoesNotExist:
            return JsonResponse(
                {'detail': 'API key inválida o negocio inactivo'},
                status=401
            )

        return self.get_response(request)

    def _es_publica(self, path: str) -> bool:
        if path in self.RUTAS_PUBLICAS:
            return True
        return any(path.startswith(p) for p in self.PREFIJOS_PUBLICOS)
