from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Applicant

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'position_applied', 'email', 'phone', 
        'state', 'cv_link', 'receipt_link', 'created_at'
    ]
    
    list_filter = [
        'position_applied', 'state', 'created_at'
    ]
    
    search_fields = [
        'full_name', 'email', 'phone'
    ]
    
    readonly_fields = ['created_at']
    
    ordering = ['-created_at']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone', 'address', 'state')
        }),
        ('Application Details', {
            'fields': ('position_applied', 'cv', 'receipt')
        }),
        ('System Information', {
            'fields': ('created_at',)
        }),
    )
    
    def cv_link(self, obj):
        if obj.cv:
            return format_html(
                '<a href="{}" target="_blank">📄 View CV</a>',
                obj.cv.url
            )
        return "No CV"
    cv_link.short_description = 'CV'
    
    def receipt_link(self, obj):
        if obj.receipt:
            return format_html(
                '<a href="{}" target="_blank">🧾 View Receipt</a>',
                obj.receipt.url
            )
        return "No Receipt"
    receipt_link.short_description = 'Receipt'
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }

# Customize admin site
admin.site.site_header = 'S MAHI Global Services - HR Dashboard'
admin.site.site_title = 'S MAHI HR'
admin.site.index_title = 'Job Applications Management'