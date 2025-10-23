from django.contrib import admin
from .models import PaymentTransaction, FormAccess

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['reference', 'email', 'amount', 'status', 'access_granted', 'created_at']
    list_filter = ['status', 'access_granted', 'created_at']
    search_fields = ['email', 'reference']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('email', 'amount', 'reference', 'status')
        }),
        ('Access Control', {
            'fields': ('access_granted',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(FormAccess)
class FormAccessAdmin(admin.ModelAdmin):
    list_display = ['email', 'payment_reference', 'access_expires', 'is_active', 'created_at']
    list_filter = ['is_active', 'access_expires', 'created_at']
    search_fields = ['email', 'payment_reference']
    readonly_fields = ['created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Access Information', {
            'fields': ('email', 'payment_reference')
        }),
        ('Access Control', {
            'fields': ('access_expires', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_access(self, obj):
        from django.utils import timezone
        return obj.is_active and obj.access_expires > timezone.now()
    has_access.boolean = True
    has_access.short_description = 'Has Access'