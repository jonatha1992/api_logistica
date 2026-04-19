from django.core.management.base import BaseCommand
from apps.tenants.models import Negocio
from apps.emails.models import PlantillaEmail

# ─── Shared inline CSS base ────────────────────────────────────────────────────
_BASE_CSS = """
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }
    .container { background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
    .header { text-align: center; color: white; padding: 30px 20px; border-radius: 10px 10px 0 0; margin: -30px -30px 20px -30px; }
    .header h1 { margin: 10px 0 0 0; font-size: 24px; }
    .footer { text-align: center; padding: 20px 0; border-top: 1px solid #eee; color: #666; font-size: 13px; }
    .btn { display: inline-block; padding: 13px 26px; color: white; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold; font-size: 15px; }
"""

# ─── Template definitions ───────────────────────────────────────────────────────
PLANTILLAS = [
    # 1. Bienvenida (registro de cuenta)
    {
        'slug': 'bienvenida',
        'asunto': '¡Bienvenido a {{ negocio_nombre }}, {{ nombre }}!',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background-color: {{ negocio_color_primario }};">
    <div style="font-size:42px;">{{ negocio_icono }}</div>
    <h1>¡Bienvenido a {{ negocio_nombre }}!</h1>
    {% if negocio_slogan %}<p style="margin:6px 0 0 0;opacity:0.9;">{{ negocio_slogan }}</p>{% endif %}
  </div>
  <p style="font-size:17px;">Hola <strong>{{ nombre }}</strong>,</p>
  <div style="background:#f8f9ff;border:2px solid {{ negocio_color_primario }};border-radius:8px;padding:20px;margin:20px 0;text-align:center;">
    <h2 style="color:{{ negocio_color_primario }};margin-top:0;">🎉 ¡Tu cuenta fue creada exitosamente!</h2>
    <p style="margin-bottom:0;">Gracias por unirte a {{ negocio_nombre }}.</p>
  </div>
  {% if link %}
  <div style="text-align:center;margin:30px 0;">
    <a href="{{ link }}" class="btn" style="background-color:{{ negocio_color_primario }};">Activar mi cuenta</a>
  </div>
  {% endif %}
  <p style="color:#666;font-size:14px;">¿Necesitás ayuda?
  {% if negocio_email_soporte %}Contactanos en <a href="mailto:{{ negocio_email_soporte }}">{{ negocio_email_soporte }}</a>.{% endif %}</p>
  <div class="footer">
    <p><strong>{{ negocio_nombre }}</strong>{% if negocio_texto_footer %} — {{ negocio_texto_footer }}{% endif %}</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Todos los derechos reservados.</p>
  </div>
</div></body></html>''',
    },

    # 2. Verificación de email
    {
        'slug': 'verificacion-email',
        'asunto': 'Verificá tu cuenta en {{ negocio_nombre }}',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background-color: {{ negocio_color_primario }};">
    <div style="font-size:42px;">✉️</div>
    <h1>Verificá tu cuenta</h1>
    <p style="margin:5px 0 0 0;opacity:0.9;">{{ negocio_nombre }}</p>
  </div>
  <p>¡Hola <strong>{{ nombre }}</strong>!</p>
  <p>Para completar tu registro en <strong>{{ negocio_nombre }}</strong>, necesitamos verificar tu dirección de email.</p>
  <div style="text-align:center;margin:30px 0;">
    <a href="{{ verification_link }}" class="btn" style="background-color:{{ negocio_color_primario }};">Verificar mi cuenta</a>
  </div>
  <p style="font-size:13px;color:#666;">
    O copiá y pegá este enlace en tu navegador:<br>
    <a href="{{ verification_link }}" style="color:{{ negocio_color_primario }};word-break:break-all;">{{ verification_link }}</a>
  </p>
  <div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:15px;margin:20px 0;font-size:14px;color:#856404;">
    <strong>⚠️ Importante:</strong> Si no creaste esta cuenta, podés ignorar este correo. El enlace expira en 24 horas.
  </div>
  <div class="footer">
    <p><strong>{{ negocio_nombre }}</strong>{% if negocio_texto_footer %} — {{ negocio_texto_footer }}{% endif %}</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Todos los derechos reservados.</p>
  </div>
</div></body></html>''',
    },

    # 3. Recupero de contraseña
    {
        'slug': 'recupero-clave',
        'asunto': 'Recuperá tu contraseña en {{ negocio_nombre }}',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background-color: {{ negocio_color_primario }};">
    <h1>🔐 Recuperación de Contraseña</h1>
    <p style="margin:5px 0 0 0;opacity:0.9;">{{ negocio_nombre }}</p>
  </div>
  <p>Hola <strong>{{ nombre }}</strong>,</p>
  <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en <strong>{{ negocio_nombre }}</strong>.</p>
  <div style="text-align:center;margin:30px 0;">
    <a href="{{ link }}" class="btn" style="background-color:{{ negocio_color_primario }};">Restablecer Contraseña</a>
  </div>
  <p>Si no solicitaste este cambio, podés ignorar este correo. Tu contraseña no cambiará.</p>
  <hr style="border:none;border-top:1px solid #eee;margin:25px 0;">
  <p style="font-size:12px;color:#999;">Si el botón no funciona, copiá este enlace en tu navegador:</p>
  <p style="word-break:break-all;color:{{ negocio_color_primario }};font-size:12px;">{{ link }}</p>
  <div class="footer">
    <p><strong>{{ negocio_nombre }}</strong>{% if negocio_texto_footer %} — {{ negocio_texto_footer }}{% endif %}</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Todos los derechos reservados.</p>
  </div>
</div></body></html>''',
    },

    # 4. Pago confirmado
    {
        'slug': 'pago-confirmado',
        'asunto': 'Pago confirmado — ${{ amount }} | {{ negocio_nombre }}',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background-color: {{ negocio_color_primario }};">
    <div style="font-size:42px;">✅</div>
    <h1>Pago Confirmado</h1>
    <p style="margin:5px 0 0 0;opacity:0.9;">{{ negocio_nombre }}</p>
  </div>
  {% if nombre %}<p>Hola <strong>{{ nombre }}</strong>,</p>{% endif %}
  <p>Tu pago fue procesado exitosamente. Aquí están los detalles:</p>
  <table style="width:100%;border-collapse:collapse;margin:20px 0;">
    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9;width:40%"><strong>Monto</strong></td>
        <td style="padding:10px;border:1px solid #ddd;font-size:18px;font-weight:bold;color:#00b894;">${{ amount }}</td></tr>
    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9"><strong>Descripción</strong></td>
        <td style="padding:10px;border:1px solid #ddd;">{{ description }}</td></tr>
    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9"><strong>Referencia</strong></td>
        <td style="padding:10px;border:1px solid #ddd;font-family:monospace;">{{ external_reference }}</td></tr>
    {% if payment_id %}
    <tr><td style="padding:10px;border:1px solid #ddd;background:#f9f9f9"><strong>ID de Pago</strong></td>
        <td style="padding:10px;border:1px solid #ddd;font-family:monospace;">{{ payment_id }}</td></tr>
    {% endif %}
  </table>
  {% if negocio_email_soporte %}
  <p style="color:#666;font-size:14px;">¿Tenés alguna consulta? Contactanos en <a href="mailto:{{ negocio_email_soporte }}">{{ negocio_email_soporte }}</a>.</p>
  {% endif %}
  <div class="footer">
    <p><strong>{{ negocio_nombre }}</strong>{% if negocio_texto_footer %} — {{ negocio_texto_footer }}{% endif %}</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Todos los derechos reservados.</p>
  </div>
</div></body></html>''',
    },

    # 5. Bienvenida suscripción premium
    {
        'slug': 'bienvenida-suscripcion',
        'asunto': '¡Tu suscripción {{ plan_name }} está activa! | {{ negocio_nombre }}',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background-color: {{ negocio_color_primario }};">
    <div style="font-size:32px;font-weight:bold;">{{ negocio_icono }} {{ negocio_nombre }}</div>
    <h1 style="margin-top:8px;">¡Bienvenido a Premium!</h1>
    <p style="margin:5px 0 0 0;opacity:0.9;">Tu suscripción está activa</p>
  </div>
  <div style="background:#00b894;color:white;padding:15px;border-radius:25px;text-align:center;margin:20px 0;font-weight:bold;font-size:17px;">
    ✅ ¡Felicidades, {{ nombre }}! Ya sos parte del plan Premium
  </div>
  <p>¡Gracias por suscribirte a <strong>{{ negocio_nombre }}</strong>! Tu plan ha sido activado.</p>
  <div style="background:#f8f9ff;border:1px solid #e0e6ff;border-radius:8px;padding:25px;margin:25px 0;">
    <h3 style="margin-top:0;">📋 Detalles de tu Suscripción</h3>
    <p><strong>Plan:</strong> {{ plan_name }}</p>
    <p><strong>Precio:</strong> <span style="font-size:22px;font-weight:bold;color:#00b894;">${{ plan_price }}</span></p>
    <p><strong>Fecha de Activación:</strong> {{ activation_date }}</p>
  </div>
  {% if frontend_url %}
  <div style="text-align:center;margin:30px 0;">
    <a href="{{ frontend_url }}" class="btn" style="background-color:{{ negocio_color_primario }};">🚀 Comenzar Ahora</a>
  </div>
  {% endif %}
  <div class="footer">
    <p><strong>{{ negocio_nombre }}</strong>{% if negocio_texto_footer %} — {{ negocio_texto_footer }}{% endif %}</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Todos los derechos reservados.</p>
    {% if negocio_email_soporte %}
    <p>Soporte: <a href="mailto:{{ negocio_email_soporte }}">{{ negocio_email_soporte }}</a></p>
    {% endif %}
  </div>
</div></body></html>''',
    },

    # 6. Confirmación de contacto (al usuario)
    {
        'slug': 'confirmacion-contacto',
        'asunto': 'Recibimos tu mensaje — {{ negocio_nombre }}',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background-color: {{ negocio_color_primario }};">
    <div style="font-size:28px;font-weight:bold;">{{ negocio_icono }} {{ negocio_nombre }}</div>
    <h1 style="margin-top:8px;">💬 ¡Mensaje Recibido!</h1>
  </div>
  <p>Hola <strong>{{ nombre }}</strong>,</p>
  <p>Gracias por contactarnos. Recibimos tu mensaje y nuestro equipo ya está revisándolo.</p>
  <div style="background:#f8f9ff;border:1px solid #e0e6ff;border-radius:8px;padding:20px;margin:20px 0;">
    <h3 style="margin-top:0;">📩 Tu mensaje:</h3>
    <p><strong>Nombre:</strong> {{ nombre }}</p>
    <p><strong>Email:</strong> {{ email }}</p>
    {% if phone %}<p><strong>Teléfono:</strong> {{ phone }}</p>{% endif %}
    <p><strong>Mensaje:</strong></p>
    <p style="white-space:pre-line;">{{ message }}</p>
    <p><strong>Fecha:</strong> {{ created_at }}</p>
  </div>
  <div style="background:#e8f5e8;border:1px solid #c3e6c3;border-radius:8px;padding:15px;margin:20px 0;">
    <p style="margin:0;"><strong>🔍 Estado:</strong> En revisión por soporte</p>
    <p style="margin:5px 0 0 0;"><strong>⏰ Tiempo de respuesta:</strong> Dentro de las próximas 24 horas</p>
    <p style="margin:5px 0 0 0;"><strong>📧 Te contactaremos a:</strong> {{ email }}</p>
  </div>
  {% if frontend_url %}
  <div style="text-align:center;">
    <a href="{{ frontend_url }}" class="btn" style="background-color:{{ negocio_color_primario }};">Volver a {{ negocio_nombre }}</a>
  </div>
  {% endif %}
  <div class="footer">
    <p>Este es un mensaje automático, por favor no respondas a este email.</p>
    <p><strong>{{ negocio_nombre }}</strong>{% if negocio_texto_footer %} — {{ negocio_texto_footer }}{% endif %}</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Todos los derechos reservados.</p>
  </div>
</div></body></html>''',
    },

    # 7. Notificación de contacto (al admin)
    {
        'slug': 'notificacion-contacto-admin',
        'asunto': '[{{ negocio_nombre }} Admin] Nuevo mensaje de contacto — {{ nombre }}',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background:linear-gradient(135deg,#ff6b6b 0%,#ee5a24 100%);">
    <div style="font-size:28px;font-weight:bold;">{{ negocio_icono }} {{ negocio_nombre }} Admin</div>
    <h1 style="margin-top:8px;">💬 Nuevo Mensaje de Contacto</h1>
  </div>
  <div style="background:#fff3cd;border:1px solid #ffeaa7;border-radius:8px;padding:15px;margin:20px 0;">
    <strong>🚨 ACCIÓN REQUERIDA:</strong> Nuevo mensaje recibido que requiere respuesta.
  </div>
  <div style="background:#f8f9ff;border:1px solid #e0e6ff;border-radius:8px;padding:20px;margin:20px 0;">
    <h3 style="margin-top:0;">👤 Información del Contacto</h3>
    <p><strong>Nombre:</strong> {{ nombre }}</p>
    <p><strong>Email:</strong> <a href="mailto:{{ email }}">{{ email }}</a></p>
    {% if phone %}<p><strong>Teléfono:</strong> <a href="tel:{{ phone }}">{{ phone }}</a></p>{% endif %}
    <p><strong>Fecha:</strong> {{ created_at }}</p>
    {% if message_id %}<p><strong>ID:</strong> #{{ message_id }}</p>{% endif %}
  </div>
  <div style="background:#fff5f5;border:1px solid #fed7d7;border-radius:8px;padding:20px;margin:20px 0;">
    <h3 style="margin-top:0;">💬 Mensaje</h3>
    <div style="white-space:pre-line;font-style:italic;padding:15px;background:white;border-radius:5px;">{{ message }}</div>
  </div>
  <div style="text-align:center;margin:30px 0;">
    <a href="mailto:{{ email }}?subject=Re: Tu consulta en {{ negocio_nombre }}" style="display:inline-block;padding:12px 24px;background:linear-gradient(135deg,#0984e3 0%,#74b9ff 100%);color:white;text-decoration:none;border-radius:25px;margin:0 8px;font-weight:bold;">
      📧 Responder Email
    </a>
    {% if phone %}
    <a href="tel:{{ phone }}" style="display:inline-block;padding:12px 24px;background:linear-gradient(135deg,#00b894 0%,#00cec9 100%);color:white;text-decoration:none;border-radius:25px;margin:0 8px;font-weight:bold;">
      📞 Llamar
    </a>
    {% endif %}
  </div>
  <div class="footer">
    <p><strong>{{ negocio_nombre }}</strong> — Panel de Administración</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Sistema de notificaciones automáticas.</p>
  </div>
</div></body></html>''',
    },

    # 8. Notificación de nueva suscripción (al admin)
    {
        'slug': 'notificacion-suscripcion-admin',
        'asunto': '[{{ negocio_nombre }} Admin] 🎉 Nueva suscripción — {{ user_name }} ({{ plan_name }})',
        'cuerpo_html': '''<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><style>''' + _BASE_CSS + '''</style></head>
<body><div class="container">
  <div class="header" style="background:linear-gradient(135deg,#00b894 0%,#00cec9 100%);">
    <div style="font-size:28px;font-weight:bold;">💰 {{ negocio_nombre }} Admin</div>
    <h1 style="margin-top:8px;">Nueva Suscripción</h1>
    <p style="margin:5px 0 0 0;opacity:0.9;">¡Un nuevo usuario se ha suscrito!</p>
  </div>
  <div style="background:linear-gradient(135deg,#fdcb6e 0%,#f39c12 100%);color:white;padding:18px;border-radius:8px;text-align:center;margin:20px 0;font-weight:bold;font-size:17px;">
    🎉 ¡NUEVA VENTA! — Plan {{ plan_name }}
  </div>
  <div style="background:#fff5f5;border:1px solid #fed7d7;border-radius:8px;padding:25px;margin:25px 0;">
    <h3 style="margin-top:0;">👤 Información del Cliente</h3>
    <p><strong>Nombre:</strong> {{ user_name }}</p>
    <p><strong>Email:</strong> <a href="mailto:{{ user_email }}">{{ user_email }}</a></p>
  </div>
  <div style="background:#f8f9ff;border:1px solid #e0e6ff;border-radius:8px;padding:25px;margin:25px 0;">
    <h3 style="margin-top:0;">📋 Detalles de la Suscripción</h3>
    <p><strong>Plan:</strong> {{ plan_name }}</p>
    <p><strong>Precio:</strong> <span style="font-size:22px;font-weight:bold;color:#00b894;">${{ plan_price }}</span></p>
    <p><strong>Estado:</strong> <span style="color:#00b894;font-weight:bold;">✅ ACTIVA</span></p>
  </div>
  <div style="display:flex;justify-content:space-around;background:#f1f2f6;padding:20px;border-radius:8px;margin:20px 0;text-align:center;">
    <div>
      <div style="font-size:24px;font-weight:bold;color:{{ negocio_color_primario }};">{{ total_subscriptions }}</div>
      <div style="font-size:12px;color:#666;text-transform:uppercase;">Suscripciones Totales</div>
    </div>
    <div>
      <div style="font-size:24px;font-weight:bold;color:{{ negocio_color_primario }};">${{ monthly_revenue }}</div>
      <div style="font-size:12px;color:#666;text-transform:uppercase;">Ingresos del Mes</div>
    </div>
  </div>
  <div class="footer">
    <p><strong>{{ negocio_nombre }}</strong> — Panel de Administración</p>
    <p>© {{ current_year }} {{ negocio_nombre }}. Sistema de notificaciones automáticas.</p>
  </div>
</div></body></html>''',
    },
]


class Command(BaseCommand):
    help = (
        'Crea las plantillas de email genéricas por defecto para todos los negocios activos. '
        'Usa variables Jinja2 de marca ({{ negocio_nombre }}, {{ negocio_color_primario }}, etc.) '
        'que se inyectan automáticamente desde la configuración del negocio.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Sobreescribe las plantillas existentes con la versión genérica.',
        )

    def handle(self, *args, **options):
        forzar = options['forzar']
        negocios = Negocio.objects.filter(activo=True)

        if not negocios.exists():
            self.stderr.write('No hay negocios activos. Creá al menos uno en /admin primero.')
            return

        creadas = 0
        actualizadas = 0

        for negocio in negocios:
            self.stdout.write(f'\n[{negocio.nombre}]')
            for plantilla in PLANTILLAS:
                obj, created = PlantillaEmail.objects.get_or_create(
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
                    self.stdout.write(f'  ✅ Creada: {plantilla["slug"]}')
                elif forzar:
                    obj.asunto = plantilla['asunto']
                    obj.cuerpo_html = plantilla['cuerpo_html']
                    obj.save(update_fields=['asunto', 'cuerpo_html'])
                    actualizadas += 1
                    self.stdout.write(f'  🔄 Actualizada: {plantilla["slug"]}')
                else:
                    self.stdout.write(f'  — Ya existe: {plantilla["slug"]} (usá --forzar para sobreescribir)')

        resumen = []
        if creadas:
            resumen.append(f'{creadas} plantilla(s) creada(s)')
        if actualizadas:
            resumen.append(f'{actualizadas} plantilla(s) actualizada(s)')

        if resumen:
            self.stdout.write(self.style.SUCCESS(f'\n{" y ".join(resumen)}.'))
        else:
            self.stdout.write('\nTodos los negocios ya tienen las plantillas. Usá --forzar para regenerar.')
