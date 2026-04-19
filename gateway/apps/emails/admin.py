from django.contrib import admin
from django.utils.html import format_html
from .models import PlantillaEmail


@admin.register(PlantillaEmail)
class PlantillaEmailAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'slug', 'asunto_preview', 'activa', 'created_at']
    list_filter = ['negocio', 'activa', 'created_at']
    search_fields = ['slug', 'asunto', 'negocio__nombre']
    readonly_fields = ['created_at', 'variables_disponibles']

    fieldsets = (
        (None, {
            'fields': ('negocio', 'slug', 'activa')
        }),
        ('Contenido del Email', {
            'fields': ('asunto', 'cuerpo_html'),
            'description': (
                'Usar sintaxis Jinja2: '
                '<code>{{ nombre }}</code>, <code>{{ link }}</code>, <code>{{ amount }}</code>, '
                '<code>{{ descripcion }}</code>, <code>{{ email }}</code>'
            ),
        }),
        ('Referencia de Variables', {
            'fields': ('variables_disponibles',),
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
                attrs={'rows': 25, 'style': 'font-family: monospace; font-size: 13px;'}
            )
        },
    }

    def asunto_preview(self, obj):
        return obj.asunto[:60] + '...' if len(obj.asunto) > 60 else obj.asunto
    asunto_preview.short_description = 'Asunto'

    def variables_disponibles(self, obj):
        return format_html(
            '<table style="border-collapse:collapse">'
            '<tr><th style="padding:4px 8px;border:1px solid #ddd">Variable</th>'
            '<th style="padding:4px 8px;border:1px solid #ddd">Descripción</th></tr>'
            '<tr><td style="padding:4px 8px;border:1px solid #ddd"><code>{{{{ nombre }}}}</code></td>'
            '<td style="padding:4px 8px;border:1px solid #ddd">Nombre del destinatario</td></tr>'
            '<tr><td style="padding:4px 8px;border:1px solid #ddd"><code>{{{{ link }}}}</code></td>'
            '<td style="padding:4px 8px;border:1px solid #ddd">URL de acción principal</td></tr>'
            '<tr><td style="padding:4px 8px;border:1px solid #ddd"><code>{{{{ amount }}}}</code></td>'
            '<td style="padding:4px 8px;border:1px solid #ddd">Monto de la transacción</td></tr>'
            '<tr><td style="padding:4px 8px;border:1px solid #ddd"><code>{{{{ descripcion }}}}</code></td>'
            '<td style="padding:4px 8px;border:1px solid #ddd">Descripción del item</td></tr>'
            '<tr><td style="padding:4px 8px;border:1px solid #ddd"><code>{{{{ email }}}}</code></td>'
            '<td style="padding:4px 8px;border:1px solid #ddd">Email del cliente</td></tr>'
            '</table>'
        )
    variables_disponibles.short_description = 'Variables Jinja2 disponibles'
