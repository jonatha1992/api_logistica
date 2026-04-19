from django.contrib import admin
from django.utils.html import format_html
from .models import Negocio


@admin.register(Negocio)
class NegocioAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'razon_social', 'api_key_preview', 'mp_configurado',
        'smtp_configurado', 'activo', 'created_at'
    ]
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'razon_social', 'cuit']
    readonly_fields = ['api_key', 'created_at']
    actions = ['activar_negocios', 'desactivar_negocios']

    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'razon_social', 'cuit', 'activo', 'api_key', 'created_at')
        }),
        ('Contacto y Datos', {
            'fields': ('telefono', 'direccion', 'sitio_web'),
            'classes': ('collapse',),
        }),
        ('Identidad de Marca', {
            'fields': ('nombre_comercial', 'slogan', 'icono_emoji', 'email_soporte', 'texto_footer'),
            'classes': ('collapse',),
            'description': (
                'Estos campos se inyectan automáticamente en todos los templates de email como variables Jinja2. '
                'Variables disponibles: <code>{{ negocio_nombre }}</code>, <code>{{ negocio_slogan }}</code>, '
                '<code>{{ negocio_icono }}</code>, <code>{{ negocio_color_primario }}</code>, '
                '<code>{{ negocio_logo_url }}</code>, <code>{{ negocio_sitio_web }}</code>, '
                '<code>{{ negocio_email_soporte }}</code>, <code>{{ negocio_texto_footer }}</code>'
            ),
        }),
        ('Branding Visual', {
            'fields': ('logo_url', 'color_primario', 'color_secundario'),
            'classes': ('collapse',),
            'description': 'URL pública del logo (HTTPS). Colores en formato hexadecimal, ej: #4f46e5',
        }),
        ('🏦 Mercado Pago', {
            'fields': ('mp_access_token', 'webhook_notificacion'),
            'classes': ('collapse',),
            'description': (
                '⚠️ El token se encripta automáticamente con Fernet al guardar. '
                'Nunca se almacena en texto plano en la base de datos.'
            ),
        }),
        ('📨 Proveedores de Email', {
            'fields': ('resend_api_key', 'smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'smtp_from'),
            'classes': ('collapse',),
            'description': (
                '<strong>Resend (recomendado):</strong> Agregá el API Key de resend.com — se encripta automáticamente. '
                'Si está configurado, se usa Resend para enviar emails (ignorando SMTP).<br>'
                '<strong>SMTP (fallback):</strong> Se usa si no hay API Key de Resend configurado. '
                'La contraseña SMTP también se encripta automáticamente.'
            ),
        }),
    )

    def api_key_preview(self, obj):
        return format_html(
            '<code style="background:#f0f0f0;padding:2px 6px;border-radius:3px">'
            '{}...</code>',
            obj.api_key[:12]
        )
    api_key_preview.short_description = 'API Key'

    def mp_configurado(self, obj):
        return bool(obj.mp_access_token)
    mp_configurado.boolean = True
    mp_configurado.short_description = 'MP ✓'

    def smtp_configurado(self, obj):
        return bool(obj.smtp_host and obj.smtp_user)
    smtp_configurado.boolean = True
    smtp_configurado.short_description = 'SMTP ✓'

    @admin.action(description='✅ Activar negocios seleccionados')
    def activar_negocios(self, request, queryset):
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} negocio(s) activado(s).')

    @admin.action(description='❌ Desactivar negocios seleccionados')
    def desactivar_negocios(self, request, queryset):
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} negocio(s) desactivado(s).')
