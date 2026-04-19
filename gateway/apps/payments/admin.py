from django.contrib import admin
from django.utils.html import format_html
from .models import Transaccion


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = [
        'negocio', 'external_reference', 'amount_display',
        'status_badge', 'customer_email', 'created_at'
    ]
    list_filter = ['status', 'negocio', 'created_at']
    search_fields = ['external_reference', 'customer_email', 'payment_id', 'preference_id']
    date_hierarchy = 'created_at'
    readonly_fields = [
        'negocio', 'preference_id', 'payment_id', 'external_reference',
        'amount', 'description', 'customer_email', 'status',
        'init_point', 'metadata_json', 'created_at', 'updated_at'
    ]

    def amount_display(self, obj):
        return f'$ {obj.amount:,.2f}'
    amount_display.short_description = 'Monto'
    amount_display.admin_order_field = 'amount'

    def status_badge(self, obj):
        colors = {
            'approved': '#28a745',
            'pending': '#ffc107',
            'rejected': '#dc3545',
            'cancelled': '#6c757d',
            'in_process': '#17a2b8',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:12px;font-size:11px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'

    def has_add_permission(self, request):
        return False  # Las transacciones solo se crean via API

    def has_delete_permission(self, request, obj=None):
        return False
