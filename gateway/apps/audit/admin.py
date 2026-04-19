from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['negocio', 'method_badge', 'endpoint', 'status_code_display', 'created_at']
    list_filter = ['negocio', 'method', 'status_code']
    search_fields = ['endpoint', 'error_message']
    date_hierarchy = 'created_at'
    readonly_fields = ['negocio', 'endpoint', 'method', 'status_code', 'error_message', 'created_at']

    def method_badge(self, obj):
        from django.utils.html import format_html
        colors = {'GET': '#17a2b8', 'POST': '#28a745', 'PUT': '#ffc107', 'DELETE': '#dc3545'}
        color = colors.get(obj.method, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:1px 6px;'
            'border-radius:3px;font-size:11px;font-weight:bold">{}</span>',
            color, obj.method
        )
    method_badge.short_description = 'Método'

    def status_code_display(self, obj):
        from django.utils.html import format_html
        if not obj.status_code:
            return '-'
        color = '#28a745' if obj.status_code < 400 else '#dc3545'
        return format_html(
            '<span style="color:{};font-weight:bold">{}</span>',
            color, obj.status_code
        )
    status_code_display.short_description = 'Status'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
