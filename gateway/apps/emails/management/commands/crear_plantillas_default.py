from django.core.management.base import BaseCommand
from apps.tenants.models import Negocio
from apps.emails.models import PlantillaEmail

PLANTILLAS = [
    {
        'slug': 'bienvenida',
        'asunto': 'Bienvenido, {{ nombre }}',
        'cuerpo_html': '''<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
  <h2 style="color:#333">¡Bienvenido, {{ nombre }}!</h2>
  <p>Tu cuenta fue creada exitosamente.</p>
  {% if link %}
  <p><a href="{{ link }}" style="background:#007bff;color:white;padding:10px 20px;text-decoration:none;border-radius:4px">Activar cuenta</a></p>
  {% endif %}
  <hr>
  <p style="color:#999;font-size:12px">Este es un email automático, no respondas a este mensaje.</p>
</body>
</html>''',
    },
    {
        'slug': 'pago-confirmado',
        'asunto': 'Pago confirmado — ${{ amount }}',
        'cuerpo_html': '''<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
  <h2 style="color:#28a745">✅ Pago confirmado</h2>
  <p>Tu pago fue procesado exitosamente.</p>
  <table style="width:100%;border-collapse:collapse;margin:20px 0">
    <tr><td style="padding:8px;border:1px solid #ddd;background:#f9f9f9"><strong>Monto</strong></td>
        <td style="padding:8px;border:1px solid #ddd">${{ amount }}</td></tr>
    <tr><td style="padding:8px;border:1px solid #ddd;background:#f9f9f9"><strong>Descripción</strong></td>
        <td style="padding:8px;border:1px solid #ddd">{{ description }}</td></tr>
    <tr><td style="padding:8px;border:1px solid #ddd;background:#f9f9f9"><strong>Referencia</strong></td>
        <td style="padding:8px;border:1px solid #ddd">{{ external_reference }}</td></tr>
  </table>
  <hr>
  <p style="color:#999;font-size:12px">Este es un email automático, no respondas a este mensaje.</p>
</body>
</html>''',
    },
    {
        'slug': 'recupero-clave',
        'asunto': 'Recuperá tu contraseña',
        'cuerpo_html': '''<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
  <h2 style="color:#333">Recuperar contraseña</h2>
  <p>Hola {{ nombre }}, recibimos una solicitud para restablecer tu contraseña.</p>
  <p><a href="{{ link }}" style="background:#dc3545;color:white;padding:10px 20px;text-decoration:none;border-radius:4px">Restablecer contraseña</a></p>
  <p style="color:#999;font-size:12px">Si no solicitaste esto, ignorá este email. El link expira en 24hs.</p>
</body>
</html>''',
    },
]


class Command(BaseCommand):
    help = 'Crea las plantillas de email por defecto (bienvenida, pago-confirmado, recupero-clave) para todos los negocios que no las tengan.'

    def handle(self, *args, **options):
        negocios = Negocio.objects.filter(activo=True)
        if not negocios.exists():
            self.stderr.write('No hay negocios activos. Creá al menos uno en /admin primero.')
            return

        creadas = 0
        for negocio in negocios:
            for plantilla in PLANTILLAS:
                _, created = PlantillaEmail.objects.get_or_create(
                    negocio=negocio,
                    slug=plantilla['slug'],
                    defaults={
                        'asunto': plantilla['asunto'],
                        'cuerpo_html': plantilla['cuerpo_html'],
                        'activa': True,
                    }
                )
                if created:
                    creadas += 1
                    self.stdout.write(f'  Creada: [{negocio.nombre}] {plantilla["slug"]}')

        if creadas:
            self.stdout.write(self.style.SUCCESS(f'\n{creadas} plantilla(s) creada(s).'))
        else:
            self.stdout.write('Todos los negocios ya tienen las plantillas por defecto.')
