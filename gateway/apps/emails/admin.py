from django.contrib import admin
from .models import PlantillaEmail


@admin.register(PlantillaEmail)
class PlantillaEmailAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'slug', 'asunto_preview', 'activa', 'created_at']
    list_filter = ['negocio', 'activa']
    search_fields = ['slug', 'asunto']
    readonly_fields = ['created_at']

    fieldsets = (
        (None, {
            'fields': ('negocio', 'slug', 'activa')
        }),
        ('Contenido del Email', {
            'fields': ('asunto', 'cuerpo_html'),
            'description': (
                'Usar sintaxis Jinja2 para variables dinámicas: '
                '<code>{{ nombre }}</code>, <code>{{ link }}</code>, <code>{{ amount }}</code>'
            ),
        }),
        ('Información', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def asunto_preview(self, obj):
        return obj.asunto[:60] + '...' if len(obj.asunto) > 60 else obj.asunto
    asunto_preview.short_description = 'Asunto'
