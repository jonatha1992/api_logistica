from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import PlantillaEmail


@admin.register(PlantillaEmail)
class PlantillaEmailAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'slug', 'asunto_preview', 'activa', 'created_at']
    list_filter = ['negocio', 'activa', 'created_at']
    search_fields = ['slug', 'asunto', 'negocio__nombre']
    readonly_fields = ['created_at', 'variables_marca', 'variables_comunes']

    fieldsets = (
        (None, {
            'fields': ('negocio', 'slug', 'activa'),
        }),
        ('Contenido del Email', {
            'fields': ('asunto', 'cuerpo_html'),
            'description': (
                'Usar sintaxis <strong>Jinja2</strong>: '
                '<code>{{ variable }}</code> para variables, '
                '<code>{% if condicion %}...{% endif %}</code> para condicionales.<br>'
                'Las variables de marca del negocio se inyectan automáticamente en cada envío.'
            ),
        }),
        ('🎨 Variables de Marca (auto-inyectadas)', {
            'fields': ('variables_marca',),
            'description': 'Estas variables se agregan automáticamente desde la configuración del negocio.',
        }),
        ('📋 Variables de Contenido (por plantilla)', {
            'fields': ('variables_comunes',),
            'classes': ('collapse',),
        }),
        ('Información', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    formfield_overrides = {
        __import__('django.db.models', fromlist=['TextField']).TextField: {
            'widget': __import__('django.forms', fromlist=['Textarea']).Textarea(
                attrs={'rows': 28, 'style': 'font-family: monospace; font-size: 13px;'}
            )
        },
    }

    def asunto_preview(self, obj):
        return obj.asunto[:70] + '...' if len(obj.asunto) > 70 else obj.asunto
    asunto_preview.short_description = 'Asunto'

    def variables_marca(self, obj):
        rows = [
            ('{{ negocio_nombre }}', 'Nombre comercial del negocio (ej: "Mi Tienda Online")'),
            ('{{ negocio_slogan }}', 'Slogan o descripción corta del negocio'),
            ('{{ negocio_icono }}', 'Emoji/ícono para el encabezado (ej: 📦)'),
            ('{{ negocio_color_primario }}', 'Color primario en hex (ej: #4f46e5) — úsalo en estilos inline'),
            ('{{ negocio_color_secundario }}', 'Color secundario en hex (ej: #7c3aed)'),
            ('{{ negocio_logo_url }}', 'URL pública del logo del negocio'),
            ('{{ negocio_sitio_web }}', 'URL del sitio web del negocio'),
            ('{{ negocio_email_soporte }}', 'Email de soporte del negocio'),
            ('{{ negocio_texto_footer }}', 'Texto personalizado del pie de email'),
        ]
        return self._tabla_variables(rows)
    variables_marca.short_description = 'Variables de marca (siempre disponibles)'

    def variables_comunes(self, obj):
        rows_by_slug = {
            'bienvenida': [
                ('{{ nombre }}', 'Nombre del destinatario'),
                ('{{ link }}', 'URL de activación de cuenta'),
                ('{{ current_year }}', 'Año actual'),
            ],
            'verificacion-email': [
                ('{{ nombre }}', 'Nombre del destinatario'),
                ('{{ verification_link }}', 'Enlace de verificación'),
                ('{{ current_year }}', 'Año actual'),
            ],
            'recupero-clave': [
                ('{{ nombre }}', 'Nombre del destinatario'),
                ('{{ link }}', 'Enlace de restablecimiento de contraseña'),
                ('{{ current_year }}', 'Año actual'),
            ],
            'pago-confirmado': [
                ('{{ nombre }}', 'Nombre del destinatario'),
                ('{{ amount }}', 'Monto del pago'),
                ('{{ description }}', 'Descripción del pago'),
                ('{{ external_reference }}', 'Referencia externa del pago'),
                ('{{ payment_id }}', 'ID de la transacción'),
                ('{{ current_year }}', 'Año actual'),
            ],
            'bienvenida-suscripcion': [
                ('{{ nombre }}', 'Nombre del suscriptor'),
                ('{{ plan_name }}', 'Nombre del plan suscripto'),
                ('{{ plan_price }}', 'Precio del plan'),
                ('{{ activation_date }}', 'Fecha de activación'),
                ('{{ frontend_url }}', 'URL de la aplicación'),
                ('{{ current_year }}', 'Año actual'),
            ],
            'confirmacion-contacto': [
                ('{{ nombre }}', 'Nombre del contacto'),
                ('{{ email }}', 'Email del contacto'),
                ('{{ phone }}', 'Teléfono (opcional)'),
                ('{{ message }}', 'Contenido del mensaje'),
                ('{{ created_at }}', 'Fecha y hora del mensaje'),
                ('{{ frontend_url }}', 'URL de la aplicación'),
                ('{{ current_year }}', 'Año actual'),
            ],
            'notificacion-contacto-admin': [
                ('{{ nombre }}', 'Nombre del contacto'),
                ('{{ email }}', 'Email del contacto'),
                ('{{ phone }}', 'Teléfono (opcional)'),
                ('{{ message }}', 'Contenido del mensaje'),
                ('{{ message_id }}', 'ID del mensaje en el sistema'),
                ('{{ created_at }}', 'Fecha y hora'),
                ('{{ current_year }}', 'Año actual'),
            ],
            'notificacion-suscripcion-admin': [
                ('{{ user_name }}', 'Nombre del nuevo suscriptor'),
                ('{{ user_email }}', 'Email del nuevo suscriptor'),
                ('{{ plan_name }}', 'Nombre del plan'),
                ('{{ plan_price }}', 'Precio del plan'),
                ('{{ total_subscriptions }}', 'Total de suscripciones activas'),
                ('{{ monthly_revenue }}', 'Ingresos del mes'),
                ('{{ current_year }}', 'Año actual'),
            ],
        }
        rows = rows_by_slug.get(obj.slug, [
            ('{{ nombre }}', 'Nombre del destinatario'),
            ('{{ link }}', 'URL de acción principal'),
            ('{{ current_year }}', 'Año actual'),
        ])
        return self._tabla_variables(rows)
    variables_comunes.short_description = 'Variables de contenido (según slug de plantilla)'

    def _tabla_variables(self, rows):
        header = (
            '<table style="border-collapse:collapse;width:100%">'
            '<tr>'
            '<th style="padding:6px 10px;border:1px solid #ddd;background:#f5f5f5;text-align:left;">Variable Jinja2</th>'
            '<th style="padding:6px 10px;border:1px solid #ddd;background:#f5f5f5;text-align:left;">Descripción</th>'
            '</tr>'
        )
        body = ''.join(
            f'<tr>'
            f'<td style="padding:6px 10px;border:1px solid #ddd;font-family:monospace;">{var}</td>'
            f'<td style="padding:6px 10px;border:1px solid #ddd;font-size:13px;">{desc}</td>'
            f'</tr>'
            for var, desc in rows
        )
        # mark_safe instead of format_html: content is trusted literals, and format_html would
        # collapse {{ var }} Jinja2 braces to { var } via str.format(), breaking the reference table.
        return mark_safe(header + body + '</table>')
